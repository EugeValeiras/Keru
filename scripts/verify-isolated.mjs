#!/usr/bin/env node
/**
 * KER-60 · Verificación AISLADA por tarea.
 *
 * Cada tarea, al verificarse, levanta su PROPIO stack en Docker con PUERTOS EFÍMEROS y corre
 * las suites contra él, sin pisar a otras tareas (ni a los servers de dev). Elimina la clase de
 * fallo que más caro salió: puertos compartidos (:3000/:4200), "servers zombie" y falsos rojos
 * (ver la memoria keru-verify-gate del proyecto). Habilita CONCURRENCIA real: N verificaciones
 * en paralelo, cada una en su propio `docker compose -p keru-<tarea>` sin colisión de nombres
 * ni puertos.
 *
 * Qué hace (todo desde el paraguas, que ya orquesta el gate cross-repo):
 *   1. Deriva un project name único (keru-<rama/tarea sanitizada>) y resuelve los worktrees
 *      hermanos de Keru-API y Keru-Webapp de la misma tarea.
 *   2. `docker compose -p <proj> --profile app up -d --build api`  → api + postgres + redis + floci,
 *      todos con puertos de host EFÍMEROS (POSTGRES_HOST_PORT=0, etc.).
 *   3. Descubre los puertos con `docker compose -p <proj> port <svc> <puertoInterno>` y espera
 *      a que la API esté healthy (GET /api/v1/health), como el CI.
 *   4. Seedea la API aislada (ts-node, el mismo `npm run seed` del CI) apuntando a los puertos dinámicos.
 *   5. Corre las suites contra ESE stack:
 *        - unit:    `npm test`         (jest, en Keru-API)
 *        - api-e2e: `npm run test:e2e` (jest+supertest contra el postgres/redis dockerizados; DB keru_e2e aislada)
 *        - web-e2e: genera un proxy.conf al vuelo (/api→apiPort, /media→flociPort), levanta
 *                   `ng serve` en puerto EFÍMERO con ese proxy, y corre Playwright con
 *                   E2E_BASE_URL=http://127.0.0.1:<puertoWebapp>.
 *   6. TEARDOWN SIEMPRE (éxito o fallo): mata el ng serve + `docker compose -p <proj> down -v
 *      --remove-orphans` + borra los archivos temporales. `docker ps` queda limpio.
 *
 * Uso:
 *   node scripts/verify-isolated.mjs [--suite=unit,api-e2e,web-e2e] [--gate|--full]
 *                                    [--project=<name>] [--no-build] [--no-install]
 *                                    [--keep] [--api-e2e-args="<filtro jest>"]
 *
 *   --suite     Suites a correr (coma-separadas). Default: unit,api-e2e,web-e2e (todo).
 *   --gate      Atajo del gate de Kanban: unit,api-e2e (Playwright fuera del gate automático,
 *               por la política de keru-verify-gate; se corre a mano / en la demo con --full).
 *   --full      Atajo de todo: unit,api-e2e,web-e2e.
 *   --project   Forzar el project name de docker compose (default: derivado de la rama/tarea).
 *   --no-build  No pasar --build al compose up (reusar la imagen ya buildeada; reruns rápidos).
 *   --no-install Nunca correr npm ci (default: solo si falta node_modules en un worktree).
 *   --keep      No hacer teardown (dejar el stack + ng serve para inspección/debug).
 *   --api-e2e-args  Filtro extra para el jest e2e (p. ej. --api-e2e-args="first-login").
 *
 * Variables de entorno equivalentes: KERU_VERIFY_SUITE, KERU_VERIFY_PROJECT, KERU_API_DIR,
 * KERU_WEBAPP_DIR (mismos overrides que docker-compose.yml y run-webapp-e2e.mjs).
 *
 * Requisitos: Docker Desktop, Node 20, y los worktrees hermanos de Keru-API/Keru-Webapp con deps.
 * Windows: usa docker.exe + npm/ng vía shell; las rutas del host no se pasan a docker (efímero todo).
 */
import { spawn, spawnSync } from 'node:child_process';
import { closeSync, existsSync, openSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { generateKeyPairSync } from 'node:crypto';
import { dirname, join, resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { get as httpGet } from 'node:http';

const IS_WIN = process.platform === 'win32';
const __dirname = dirname(fileURLToPath(import.meta.url));

// Estado del teardown (declarado arriba para que un fail() temprano lo vea, sin TDZ).
let ngProc = null;
let ngPid = null;
const tempFiles = [];
let toreDown = false;
let stackUp = false; // true una vez que se emitió `up`: recién ahí hay algo que limpiar.

// ─────────────────────────────────────────────────────────────────────────────
// Args / config
// ─────────────────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
const hasFlag = (name) => argv.includes(`--${name}`);
const getOpt = (name, dflt) => {
  const hit = argv.find((a) => a.startsWith(`--${name}=`));
  return hit ? hit.slice(name.length + 3) : dflt;
};

let suites = getOpt('suite', process.env.KERU_VERIFY_SUITE || 'unit,api-e2e,web-e2e');
if (hasFlag('gate')) suites = 'unit,api-e2e';
if (hasFlag('full')) suites = 'unit,api-e2e,web-e2e';
const SUITES = new Set(suites.split(',').map((s) => s.trim()).filter(Boolean));

const NO_BUILD = hasFlag('no-build');
const NO_INSTALL = hasFlag('no-install');
const KEEP = hasFlag('keep');
const API_E2E_ARGS = getOpt('api-e2e-args', '');
const WEB_E2E_ARGS = getOpt('web-e2e-args', '');

// ─────────────────────────────────────────────────────────────────────────────
// Resolución de worktrees hermanos (mismo patrón que run-webapp-e2e.mjs)
// El script vive en <umbrella>/scripts/; <umbrella> puede ser un worktree
// (.../Keru/.kanban/worktrees/<slug>) o el checkout base (.../Keru).
// ─────────────────────────────────────────────────────────────────────────────
const umbrella = resolve(__dirname, '..');
const slugMatch = umbrella.replace(/\\/g, '/').match(/\.kanban\/worktrees\/([^/]+)\/?$/);
const slug = slugMatch ? slugMatch[1] : '';

function siblingCandidates(repo, marker) {
  const list = [];
  const envDir = process.env[`KERU_${repo === 'Keru-API' ? 'API' : 'WEBAPP'}_DIR`];
  if (envDir) list.push(resolve(envDir));
  if (slug) {
    // worktree hermano de la misma tarea: .../Keru/.kanban/worktrees/<slug>
    //                                   → .../Keru/<repo>/.kanban/worktrees/<slug>
    const keruRoot = umbrella.replace(/[\\/]\.kanban[\\/]worktrees[\\/][^\\/]+[\\/]?$/, '');
    list.push(join(keruRoot, repo, '.kanban', 'worktrees', slug));
    list.push(join(keruRoot, repo)); // fallback al checkout base del sub-repo
  } else {
    list.push(join(umbrella, repo)); // corriendo desde el checkout base del paraguas
  }
  return list.find((d) => existsSync(join(d, marker)));
}

const apiDir = siblingCandidates('Keru-API', 'docker-compose.yml');
const webDir = siblingCandidates('Keru-Webapp', 'playwright.config.ts');

if (!apiDir) fail('No encuentro el worktree de Keru-API (con docker-compose.yml). Probé KERU_API_DIR, el worktree hermano y el checkout base.');
if ((SUITES.has('web-e2e')) && !webDir) fail('No encuentro el worktree de Keru-Webapp (con playwright.config.ts) para la suite web-e2e.');

// Project name de docker compose: minúsculas y solo [a-z0-9_-].
const rawProject = getOpt('project', process.env.KERU_VERIFY_PROJECT || (slug ? `keru-${slug}` : gitBranch(apiDir) || 'keru-local'));
const PROJECT = rawProject.toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'keru-local';

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────
function fail(msg) {
  console.error(`\n✖ ${msg}`);
  teardown(); // TEARDOWN SIEMPRE, incluso en un fallo a mitad de camino.
  process.exit(1);
}
function log(msg) {
  console.log(`\n\x1b[36m[verify-isolated:${PROJECT}]\x1b[0m ${msg}`);
}
function gitBranch(cwd) {
  const r = spawnSync('git', ['rev-parse', '--abbrev-ref', 'HEAD'], { cwd, encoding: 'utf8', shell: true });
  return (r.stdout || '').trim();
}
// Corre un comando y hereda stdio (streaming). Devuelve el exit code.
function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { stdio: 'inherit', shell: true, ...opts });
  return r.status ?? 1;
}
// Corre y CAPTURA stdout (para descubrir puertos).
function capture(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { encoding: 'utf8', shell: true, ...opts });
  return (r.stdout || '').trim();
}
// docker compose acotado a este proyecto.
const composeBase = ['compose', '-p', PROJECT];
function compose(args, opts = {}) {
  return run('docker', [...composeBase, ...args], { cwd: apiDir, ...opts });
}
function composeCapture(args, opts = {}) {
  return capture('docker', [...composeBase, ...args], { cwd: apiDir, ...opts });
}
// Descubre el puerto de host efímero de un servicio: `port <svc> <puertoInterno>` → "0.0.0.0:PORT".
function discoverPort(svc, internal) {
  const out = composeCapture(['port', svc, String(internal)]);
  const m = out.match(/:(\d+)\s*$/m);
  if (!m) fail(`No pude descubrir el puerto de ${svc}:${internal} (salida: "${out}")`);
  return Number(m[1]);
}
// Genera un par VAPID (P-256) sin depender de web-push: como el paso "claves VAPID efímeras"
// del CI, para que la suite de push (UC-18) vea el banner. Solo vive en esta corrida.
function ephemeralVapid() {
  const { publicKey, privateKey } = generateKeyPairSync('ec', { namedCurve: 'prime256v1' });
  const pub = publicKey.export({ format: 'jwk' });
  const prv = privateKey.export({ format: 'jwk' });
  const b64u = (s) => Buffer.from(s, 'base64url');
  const raw = Buffer.concat([Buffer.from([4]), b64u(pub.x), b64u(pub.y)]);
  return { publicKey: raw.toString('base64url'), privateKey: prv.d };
}
// Poll HTTP hasta 2xx o timeout.
function waitHttp(url, timeoutMs, label) {
  return new Promise((resolve) => {
    const start = Date.now();
    const tick = () => {
      const req = httpGet(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 500) return resolve(true);
        retry();
      });
      req.on('error', retry);
      req.setTimeout(3000, () => req.destroy());
    };
    const retry = () => {
      if (Date.now() - start > timeoutMs) {
        console.error(`  … ${label} no respondió en ${Math.round(timeoutMs / 1000)}s (${url})`);
        return resolve(false);
      }
      setTimeout(tick, 1500);
    };
    tick();
  });
}
function ensureDeps(dir) {
  if (NO_INSTALL) return;
  if (!existsSync(join(dir, 'node_modules'))) {
    log(`Instalando deps (npm ci) en ${dir}…`);
    if (run('npm', ['ci'], { cwd: dir }) !== 0) fail(`npm ci falló en ${dir}`);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Teardown (siempre)
// ─────────────────────────────────────────────────────────────────────────────
function teardown() {
  if (toreDown) return;
  toreDown = true;
  if (!stackUp) return; // fallo temprano (antes del `up`): no hay stack ni ng serve que limpiar.
  if (KEEP) {
    log(`--keep: NO hago teardown. Stack "${PROJECT}" y ng serve (pid ${ngPid ?? '—'}) siguen vivos.`);
    log(`Para limpiar a mano: docker compose -p ${PROJECT} down -v --remove-orphans`);
    return;
  }
  log('Teardown (siempre): matando ng serve + docker compose down -v…');
  // 1) ng serve (y su árbol de procesos hijo).
  if (ngPid) {
    try {
      if (IS_WIN) spawnSync('taskkill', ['/F', '/T', '/PID', String(ngPid)], { stdio: 'ignore', shell: true });
      else process.kill(-ngPid, 'SIGKILL');
    } catch { /* ya muerto */ }
  }
  // 2) stack docker + volúmenes + huérfanos.
  spawnSync('docker', [...composeBase, 'down', '-v', '--remove-orphans'], { cwd: apiDir, stdio: 'inherit', shell: true });
  // 3) archivos temporales (proxy.conf, .e2e-base-url).
  for (const f of tempFiles) { try { rmSync(f, { force: true }); } catch { /* noop */ } }
}

// Teardown ante señales / excepciones no atrapadas.
for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
  process.on(sig, () => { teardown(); process.exit(130); });
}
process.on('uncaughtException', (e) => { console.error(e); teardown(); process.exit(1); });

// ─────────────────────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────────────────────
async function main() {
  log(`Suites: ${[...SUITES].join(', ')} · API=${apiDir}${webDir ? ` · Webapp=${webDir}` : ''}`);
  ensureDeps(apiDir);
  if (SUITES.has('web-e2e')) ensureDeps(webDir);

  const vapid = ephemeralVapid();
  // Env de infra para el `up`: puertos de host EFÍMEROS + throttling apagado (las suites hacen
  // muchos signups desde una IP) + claves VAPID descartables para la suite de push.
  const upEnv = {
    ...process.env,
    POSTGRES_HOST_PORT: '0',
    REDIS_HOST_PORT: '0',
    FLOCI_HOST_PORT: '0',
    API_PORT: '0',
    THROTTLE_SKIP: 'true',
    VAPID_PUBLIC_KEY: vapid.publicKey,
    VAPID_PRIVATE_KEY: vapid.privateKey,
    VAPID_SUBJECT: 'mailto:no-reply@keru.app',
  };

  // 1) Levantar el stack aislado (api arrastra postgres + redis + floci por depends_on).
  log('Levantando stack aislado (docker compose up)…');
  const upArgs = ['--profile', 'app', 'up', '-d', '--wait'];
  if (!NO_BUILD) upArgs.push('--build');
  upArgs.push('api');
  stackUp = true; // a partir de acá el teardown SÍ debe correr (aunque el up falle a medias).
  if (compose(upArgs, { env: upEnv }) !== 0) {
    // --wait puede volver !=0 si algo no llegó a healthy: seguimos igual y dejamos que el poll decida.
    log('Aviso: `up --wait` no confirmó healthy; sigo y verifico por HTTP.');
  }

  // 2) Descubrir puertos dinámicos.
  const apiPort = discoverPort('api', 3000);
  const pgPort = discoverPort('postgres', 5432);
  const redisPort = discoverPort('redis', 6379);
  const flociPort = discoverPort('floci', 4566);
  log(`Puertos dinámicos → api=${apiPort} postgres=${pgPort} redis=${redisPort} floci=${flociPort}`);

  // 3) Esperar API healthy.
  log('Esperando a que la API esté healthy…');
  if (!(await waitHttp(`http://127.0.0.1:${apiPort}/api/v1/health`, 120_000, 'API /health'))) {
    compose(['logs', '--tail=120', 'api']);
    fail('La API aislada no llegó a healthy.');
  }

  // Env común para los procesos Node del lado API (seed, e2e): apuntan a los puertos dinámicos.
  const apiEnv = {
    ...process.env,
    DB_HOST: 'localhost', DB_PORT: String(pgPort), DB_USER: 'keru', DB_PASSWORD: 'keru', DB_NAME: 'keru',
    REDIS_HOST: 'localhost', REDIS_PORT: String(redisPort),
    AWS_REGION: 'us-east-1', AWS_ENDPOINT_URL: `http://localhost:${flociPort}`,
    SES_FROM: 'no-reply@keru.app', S3_BUCKET: 'keru-media', S3_PUBLIC_URL: '/media',
    JWT_SECRET: 'dev-secret-change-me', JWT_EXPIRES: '7d',
    THROTTLE_SKIP: 'true',
    APP_BASE_URL: `http://127.0.0.1:${apiPort}`,
  };

  // 4) Seed de la API aislada (como el paso seed del CI: ts-node contra la infra publicada).
  log('Seedeando la API aislada (npm run seed)…');
  if (run('npm', ['run', 'seed'], { cwd: apiDir, env: apiEnv }) !== 0) fail('El seed falló.');

  const failures = [];

  // 5a) unit (jest) — no toca la DB, pero corre contra este worktree.
  if (SUITES.has('unit')) {
    log('Suite unit (jest)…');
    if (run('npm', ['test'], { cwd: apiDir, env: apiEnv }) !== 0) failures.push('unit');
  }

  // 5b) api-e2e (jest+supertest) — bootea su propio Nest contra el postgres/redis dockerizados;
  //     la DB keru_e2e la recrea el globalSetup (aislada de la data del seed).
  if (SUITES.has('api-e2e')) {
    log('Suite api-e2e (jest e2e contra el stack dockerizado)…');
    const e2eArgs = ['run', 'test:e2e'];
    if (API_E2E_ARGS) e2eArgs.push('--', API_E2E_ARGS);
    if (run('npm', e2eArgs, { cwd: apiDir, env: apiEnv }) !== 0) failures.push('api-e2e');
  }

  // 5c) web-e2e (Playwright) — ng serve efímero con proxy al stack aislado.
  if (SUITES.has('web-e2e')) {
    const webPort = await startNgServe(apiPort, flociPort);
    log(`Suite web-e2e (Playwright contra http://127.0.0.1:${webPort})…`);
    const pwEnv = { ...process.env, E2E_BASE_URL: `http://127.0.0.1:${webPort}` };
    const pwArgs = ['run', 'e2e'];
    if (WEB_E2E_ARGS) pwArgs.push('--', WEB_E2E_ARGS);
    if (run('npm', pwArgs, { cwd: webDir, env: pwEnv }) !== 0) failures.push('web-e2e');
  }

  if (failures.length) fail(`Suites FALLIDAS: ${failures.join(', ')}`);
  log('✔ Todas las suites verdes contra el stack aislado.');
}

// Genera proxy.conf al vuelo, levanta ng serve en puerto efímero y devuelve el puerto elegido.
//
// IMPORTANTE: la salida de ng serve va a un ARCHIVO (stdio fd), no a un pipe de Node. Node queda
// FUERA del data path: si ng serve emite mientras corremos Playwright con spawnSync (que bloquea
// el event loop), no hay backpressure ni interferencia que cuelgue la corrida. El puerto se
// descubre tailando ese archivo.
async function startNgServe(apiPort, flociPort) {
  const proxyPath = join(webDir, `proxy.conf.${PROJECT}.json`);
  const proxy = {
    '/api': { target: `http://localhost:${apiPort}`, secure: false },
    '/media': { target: `http://localhost:${flociPort}`, secure: false, pathRewrite: { '^/media': '/keru-media' } },
  };
  writeFileSync(proxyPath, JSON.stringify(proxy, null, 2));
  tempFiles.push(proxyPath);

  const ngLogPath = join(webDir, `.ng-serve.${PROJECT}.log`);
  writeFileSync(ngLogPath, '');
  tempFiles.push(ngLogPath);
  const outFd = openSync(ngLogPath, 'a');

  log('Levantando ng serve en puerto efímero con proxy generado al vuelo…');
  ngProc = spawn('npx', ['ng', 'serve', '--port', '0', '--proxy-config', basename(proxyPath)], {
    cwd: webDir,
    shell: true,
    detached: !IS_WIN, // posix: propio grupo para poder matar el árbol con kill(-pid)
    stdio: ['ignore', outFd, outFd], // salida al archivo; Node fuera del data path
    // Sin color: Angular imprime el puerto con un ANSI en medio (http://127.0.0.1:<ESC>PORT);
    // NO_COLOR lo deja en texto plano y el parseo del puerto es robusto.
    env: { ...process.env, NO_COLOR: '1', FORCE_COLOR: '0' },
  });
  ngPid = ngProc.pid;
  closeSync(outFd); // el hijo se quedó con su propia copia del fd

  let exited = false;
  ngProc.on('exit', () => { exited = true; });

  // Descubrir el puerto que Angular eligió, leyendo el log del dev server.
  const portRe = /https?:\/\/(?:localhost|127\.0\.0\.1|\[::1\]):(\d+)/i;
  let webPort = 0;
  const start = Date.now();
  while (Date.now() - start < 120_000) {
    let content = '';
    try { content = readFileSync(ngLogPath, 'utf8'); } catch { /* aún no existe */ }
    content = content.replace(/\x1b\[[0-9;]*m/g, ''); // defensa extra: quitar ANSI si igual apareciera
    const m = content.match(portRe);
    if (m) { webPort = Number(m[1]); break; }
    if (exited) break;
    await sleep(500);
  }
  if (!webPort) {
    console.error(readFileSync(ngLogPath, 'utf8').split(/\r?\n/).slice(-40).join('\n'));
    fail('No pude determinar el puerto de ng serve.');
  }

  // Esperar a que el dev server realmente atienda.
  if (!(await waitHttp(`http://127.0.0.1:${webPort}`, 120_000, 'ng serve'))) fail('ng serve no atendió a tiempo.');
  log(`ng serve escuchando en http://127.0.0.1:${webPort}`);
  return webPort;
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

main()
  .then(() => teardown())
  .catch((e) => { console.error(e); teardown(); process.exit(1); })
  .finally(() => { /* teardown ya corrió */ });
