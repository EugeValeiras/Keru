// Chequeo de docs del paraguas: los canónicos existen y los links relativos
// de los markdown resuelven a archivos del repo.
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';

const ROOT = resolve('.');

// Docs canónicos que siempre tienen que estar (los referencian los READMEs
// del paraguas y de los sub-repos).
const REQUIRED = [
  'README.md',
  'constitution.md',
  'Keru-Casos-de-Uso-MVP.md',
  'addl/docs/architect/residual-design.md',
];

// Sub-repos gitignorados (no existen en CI) y carpetas de tooling con
// ejemplos literales de markdown que no son links reales.
const SKIP_DIRS = new Set([
  '.git',
  '.github',
  '.claude',
  '.kanban',
  'node_modules',
  'Keru-API',
  'Keru-App',
  'Keru-Webapp',
]);

function mdFiles(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry)) continue;
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...mdFiles(full));
    else if (entry.endsWith('.md')) out.push(full);
  }
  return out;
}

const errors = [];

for (const doc of REQUIRED) {
  if (!existsSync(join(ROOT, doc))) errors.push(`Falta el doc canónico: ${doc}`);
}

const LINK = /\[[^\]]*\]\(([^)\s]+)\)/g;
for (const file of mdFiles(ROOT)) {
  const text = readFileSync(file, 'utf8');
  for (const [, target] of text.matchAll(LINK)) {
    if (/^(https?:|mailto:|#)/.test(target)) continue;
    const path = decodeURIComponent(target.split('#')[0]);
    if (!path) continue;
    // Links hacia los sub-repos clonados aparte: no viven en este repo.
    if (/^(\.\/)?(Keru-API|Keru-App|Keru-Webapp)\//.test(path)) continue;
    if (!existsSync(resolve(dirname(file), path))) {
      errors.push(`${relative(ROOT, file)}: link roto -> ${target}`);
    }
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log('Docs OK: canónicos presentes y links relativos válidos.');
