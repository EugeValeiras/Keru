import { Component, inject, signal } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { ApiService } from '../../core/api.service';
import { DashboardMetrics } from '../../core/models';

@Component({
  selector: 'bo-dashboard',
  imports: [MatCardModule, MatIconModule, MatProgressBarModule],
  template: `
    <h2>Panel</h2>
    @if (loading()) { <mat-progress-bar mode="indeterminate" /> }
    @if (m(); as d) {
      <div class="grid">
        <mat-card class="stat accent">
          <div class="n">{{ d.caregivers['pending'] ?? 0 }}</div>
          <div class="l"><mat-icon>hourglass_top</mat-icon> Cuidadores pendientes</div>
        </mat-card>
        <mat-card class="stat ok">
          <div class="n">{{ d.caregivers['approved'] ?? 0 }}</div>
          <div class="l"><mat-icon>verified</mat-icon> Cuidadores aprobados</div>
        </mat-card>
        <mat-card class="stat mut">
          <div class="n">{{ d.caregivers['deactivated'] ?? 0 }}</div>
          <div class="l"><mat-icon>block</mat-icon> Cuidadores desactivados</div>
        </mat-card>
        <mat-card class="stat">
          <div class="n">{{ d.activeAssignments }}</div>
          <div class="l"><mat-icon>assignment_ind</mat-icon> Asignaciones activas</div>
        </mat-card>
        <mat-card class="stat">
          <div class="n">{{ d.requests['pending'] ?? 0 }}</div>
          <div class="l"><mat-icon>pending_actions</mat-icon> Solicitudes pendientes</div>
        </mat-card>
        <mat-card class="stat">
          <div class="n">{{ d.requests['finished'] ?? 0 }}</div>
          <div class="l"><mat-icon>task_alt</mat-icon> Servicios finalizados</div>
        </mat-card>
      </div>
    }
  `,
  styles: [
    `
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 16px;
        margin-top: 12px;
      }
      .stat {
        padding: 20px;
      }
      .n {
        font-size: 40px;
        font-weight: 500;
        line-height: 1;
      }
      .l {
        margin-top: 8px;
        color: #666;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
      }
      .accent .n { color: #8a6100; }
      .ok .n { color: #1b6b3a; }
      .mut .n { color: #777; }
    `,
  ],
})
export class Dashboard {
  private readonly api = inject(ApiService);
  readonly m = signal<DashboardMetrics | null>(null);
  readonly loading = signal(false);

  constructor() {
    this.loading.set(true);
    this.api.dashboard().subscribe({
      next: (d) => this.m.set(d),
      complete: () => this.loading.set(false),
    });
  }
}
