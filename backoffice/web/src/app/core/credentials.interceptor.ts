import { HttpInterceptorFn } from '@angular/common/http';

/** Manda la cookie de sesión (httpOnly) en cada request al BFF. */
export const credentialsInterceptor: HttpInterceptorFn = (req, next) =>
  next(req.clone({ withCredentials: true }));
