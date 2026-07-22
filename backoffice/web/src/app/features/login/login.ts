import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'bo-login',
  imports: [
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressBarModule,
  ],
  template: `
    <div class="wrap">
      <mat-card class="card">
        @if (loading()) {
          <mat-progress-bar mode="indeterminate" />
        }
        <mat-card-header>
          <mat-card-title>Keru · Back-office</mat-card-title>
          <mat-card-subtitle>Acceso de administradores</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <form (ngSubmit)="submit()">
            <mat-form-field appearance="outline" class="full">
              <mat-label>Email</mat-label>
              <input matInput type="email" name="email" [(ngModel)]="email" required />
            </mat-form-field>
            <mat-form-field appearance="outline" class="full">
              <mat-label>Contraseña</mat-label>
              <input matInput type="password" name="password" [(ngModel)]="password" required />
            </mat-form-field>
            <button mat-flat-button color="primary" class="full" type="submit" [disabled]="loading()">
              Ingresar
            </button>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .wrap {
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #f4f6fb;
      }
      .card {
        width: 360px;
        padding-bottom: 16px;
      }
      .full {
        width: 100%;
      }
    `,
  ],
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly snack = inject(MatSnackBar);

  email = '';
  password = '';
  readonly loading = signal(false);

  async submit(): Promise<void> {
    if (!this.email || !this.password) return;
    this.loading.set(true);
    try {
      await this.auth.login(this.email, this.password);
      await this.router.navigateByUrl('/caregivers');
    } catch {
      this.snack.open('Credenciales inválidas o cuenta no admin', 'Cerrar', { duration: 4000 });
    } finally {
      this.loading.set(false);
    }
  }
}
