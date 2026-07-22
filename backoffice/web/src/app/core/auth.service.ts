import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { SessionUser } from './models';

/** Auth contra el BFF (cookie httpOnly). El token nunca vive en el browser. */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  readonly user = signal<SessionUser | null>(null);

  async login(email: string, password: string): Promise<void> {
    const u = await firstValueFrom(
      this.http.post<SessionUser>('/bff/auth/login', { email, password }),
    );
    this.user.set(u);
  }

  async logout(): Promise<void> {
    await firstValueFrom(this.http.post('/bff/auth/logout', {}));
    this.user.set(null);
  }

  /** Restaura la sesión desde la cookie (para el guard al recargar). */
  async tryRestore(): Promise<boolean> {
    try {
      const u = await firstValueFrom(this.http.get<SessionUser>('/bff/auth/me'));
      this.user.set(u);
      return true;
    } catch {
      this.user.set(null);
      return false;
    }
  }
}
