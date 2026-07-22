/** Configuración del BFF, leída del entorno con defaults de desarrollo. */
export const config = () => ({
  port: Number(process.env.PORT ?? 3001),
  keruApiUrl: process.env.KERU_API_URL ?? 'http://localhost:3000/api/v1',
  cookieName: process.env.COOKIE_NAME ?? 'keru_bo_session',
  cookieSecure: process.env.COOKIE_SECURE === 'true',
  webOrigin: process.env.WEB_ORIGIN ?? 'http://localhost:4200',
});

export type BffConfig = ReturnType<typeof config>;

/** Opciones de la cookie de sesión: httpOnly (no accesible por JS), sameSite lax, 7 días. */
export function sessionCookieOptions(secure: boolean) {
  return {
    httpOnly: true as const,
    secure,
    sameSite: 'lax' as const,
    path: '/',
    maxAge: 7 * 24 * 60 * 60 * 1000,
  };
}
