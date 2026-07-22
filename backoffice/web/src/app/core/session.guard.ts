import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

/** Protege las rutas del back-office: exige sesión (o intenta restaurarla desde la cookie). */
export const sessionGuard: CanActivateFn = async () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.user()) return true;
  const ok = await auth.tryRestore();
  return ok ? true : router.parseUrl('/login');
};
