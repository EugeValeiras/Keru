import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'bo-shell',
  imports: [
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
    MatToolbarModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
  ],
  template: `
    <mat-toolbar color="primary" class="top">
      <span>Keru · Back-office</span>
      <span class="spacer"></span>
      <span class="user">{{ auth.user()?.email }}</span>
      <button mat-icon-button (click)="logout()" title="Salir">
        <mat-icon>logout</mat-icon>
      </button>
    </mat-toolbar>

    <mat-sidenav-container class="container">
      <mat-sidenav mode="side" opened class="nav">
        <mat-nav-list>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active">
            <mat-icon matListItemIcon>dashboard</mat-icon>
            <span matListItemTitle>Panel</span>
          </a>
          <a mat-list-item routerLink="/caregivers" routerLinkActive="active">
            <mat-icon matListItemIcon>how_to_reg</mat-icon>
            <span matListItemTitle>Cuidadores</span>
          </a>
          <a mat-list-item routerLink="/audit" routerLinkActive="active">
            <mat-icon matListItemIcon>receipt_long</mat-icon>
            <span matListItemTitle>Auditoría</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>
      <mat-sidenav-content class="content">
        <router-outlet />
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [
    `
      .top {
        position: sticky;
        top: 0;
        z-index: 2;
      }
      .spacer {
        flex: 1 1 auto;
      }
      .user {
        font-size: 13px;
        opacity: 0.9;
        margin-right: 8px;
      }
      .container {
        height: calc(100vh - 64px);
      }
      .nav {
        width: 220px;
        border-right: 1px solid #e0e0e0;
      }
      .content {
        padding: 24px;
        background: #f4f6fb;
      }
      a.active {
        background: rgba(0, 0, 0, 0.06);
      }
    `,
  ],
})
export class Shell {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  async logout(): Promise<void> {
    await this.auth.logout();
    await this.router.navigateByUrl('/login');
  }
}
