import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../core/api.service';
import { Badges, CaregiverDetail } from '../../core/models';

@Component({
  selector: 'bo-detail',
  imports: [
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSlideToggleModule,
    MatDividerModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
  ],
  template: `
    <button mat-button (click)="back()"><mat-icon>arrow_back</mat-icon> Volver</button>
    @if (loading()) { <mat-progress-bar mode="indeterminate" /> }

    @if (c(); as cg) {
      <div class="grid">
        <mat-card>
          <mat-card-header>
            <mat-card-title>{{ cg.displayName }}</mat-card-title>
            <mat-card-subtitle>
              <span class="badge" [class]="cg.status">{{ cg.status }}</span> · {{ cg.zone }} ·
              {{ cg.rates.ratePerHour }} {{ cg.rates.currency }}/h
            </mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <h4>Especialidades</h4>
            <mat-chip-set>
              @for (s of cg.specialties; track s) { <mat-chip>{{ s }}</mat-chip> }
            </mat-chip-set>

            <h4>Modalidades</h4>
            <mat-chip-set>
              @for (m of cg.modalities; track m) { <mat-chip>{{ m }}</mat-chip> }
            </mat-chip-set>

            <h4>Certificaciones</h4>
            @if (cg.certifications.length === 0) { <p class="muted">Sin certificaciones cargadas.</p> }
            @for (cert of cg.certifications; track cert.type) {
              <div class="cert">
                <mat-icon [class.ok]="cert.verified">{{ cert.verified ? 'verified' : 'schedule' }}</mat-icon>
                <span><b>{{ cert.type }}</b> — {{ cert.institution }} ({{ cert.year }})</span>
              </div>
            }

            <h4>Disponibilidad</h4>
            @for (a of cg.availability; track $index) {
              <span class="chip">{{ dayName(a.dayOfWeek) }} {{ a.from }}–{{ a.to }}</span>
            }
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header><mat-card-title>Verificación y decisión</mat-card-title></mat-card-header>
          <mat-card-content>
            <h4>Insignias (independientes)</h4>
            <mat-slide-toggle [checked]="cg.badges.certifications" (change)="toggle('certifications', $event.checked)">
              Certificaciones verificadas
            </mat-slide-toggle>
            <mat-slide-toggle [checked]="cg.badges.identity" (change)="toggle('identity', $event.checked)">
              Identidad validada
            </mat-slide-toggle>
            <mat-slide-toggle [checked]="cg.badges.background" (change)="toggle('background', $event.checked)">
              Antecedentes
            </mat-slide-toggle>

            <mat-divider />

            @if (cg.status === 'pending') {
              <div class="actions">
                <button mat-flat-button color="primary" (click)="approve()">
                  <mat-icon>check</mat-icon> Aprobar cuenta
                </button>
                @if (!rejecting()) {
                  <button mat-stroked-button color="warn" (click)="rejecting.set(true)">
                    <mat-icon>close</mat-icon> Rechazar
                  </button>
                }
              </div>
              @if (rejecting()) {
                <mat-form-field appearance="outline" class="full">
                  <mat-label>Motivo del rechazo</mat-label>
                  <textarea matInput [(ngModel)]="reason" rows="2"></textarea>
                </mat-form-field>
                <button mat-flat-button color="warn" [disabled]="!reason" (click)="reject()">Confirmar rechazo</button>
                <button mat-button (click)="rejecting.set(false)">Cancelar</button>
              }
            } @else if (cg.status === 'rejected') {
              <p class="muted">Rechazado. Motivo: {{ cg.rejectionReason }}</p>
            } @else if (cg.status === 'deactivated') {
              <p class="muted">Desactivado — oculto del marketplace, sus asignaciones/solicitudes fueron cerradas.</p>
              <button mat-flat-button color="primary" (click)="reactivate()">
                <mat-icon>restart_alt</mat-icon> Reactivar
              </button>
            } @else {
              <p class="muted">Cuenta aprobada y visible en el marketplace.</p>
              @if (!deactivating()) {
                <button mat-stroked-button color="warn" (click)="deactivating.set(true)">
                  <mat-icon>block</mat-icon> Desactivar
                </button>
              } @else {
                <mat-form-field appearance="outline" class="full">
                  <mat-label>Motivo (opcional)</mat-label>
                  <textarea matInput [(ngModel)]="deactivateReason" rows="2"></textarea>
                </mat-form-field>
                <button mat-flat-button color="warn" (click)="deactivate()">Confirmar desactivación</button>
                <button mat-button (click)="deactivating.set(false)">Cancelar</button>
              }
            }
          </mat-card-content>
        </mat-card>
      </div>
    }
  `,
  styles: [
    `
      .grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 16px;
        margin-top: 12px;
      }
      @media (max-width: 900px) {
        .grid { grid-template-columns: 1fr; }
      }
      h4 { margin: 16px 0 6px; }
      .muted { color: #888; }
      .cert { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
      .cert mat-icon.ok { color: #2b8a3e; }
      .chip { display: inline-block; background: #eef; border-radius: 12px; padding: 2px 10px; margin: 2px; font-size: 12px; }
      mat-slide-toggle { display: block; margin: 8px 0; }
      .actions { display: flex; gap: 12px; margin: 12px 0; }
      .full { width: 100%; margin-top: 8px; }
      mat-divider { margin: 16px 0; }
      .badge { padding: 2px 10px; border-radius: 12px; font-size: 12px; text-transform: capitalize; }
      .badge.pending { background: #fff4d6; color: #8a6100; }
      .badge.approved { background: #d6f5df; color: #1b6b3a; }
      .badge.rejected { background: #fbdcdc; color: #9b2222; }
    `,
  ],
})
export class Detail {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly snack = inject(MatSnackBar);

  readonly c = signal<CaregiverDetail | null>(null);
  readonly loading = signal(false);
  readonly rejecting = signal(false);
  readonly deactivating = signal(false);
  reason = '';
  deactivateReason = '';

  private readonly id = this.route.snapshot.paramMap.get('id')!;

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.api.caregiver(this.id).subscribe({
      next: (d) => this.c.set(d),
      error: () => this.snack.open('No se pudo cargar el cuidador', 'Cerrar', { duration: 3000 }),
      complete: () => this.loading.set(false),
    });
  }

  toggle(key: keyof Badges, value: boolean): void {
    this.api.setBadges(this.id, { [key]: value }).subscribe(() => {
      this.snack.open('Insignias actualizadas', 'Cerrar', { duration: 1500 });
      this.load();
    });
  }

  approve(): void {
    this.api.approve(this.id).subscribe(() => {
      this.snack.open('Cuidador aprobado', 'Cerrar', { duration: 2000 });
      this.load();
    });
  }

  reject(): void {
    this.api.reject(this.id, this.reason).subscribe(() => {
      this.snack.open('Cuidador rechazado', 'Cerrar', { duration: 2000 });
      this.rejecting.set(false);
      this.load();
    });
  }

  deactivate(): void {
    this.api.deactivate(this.id, this.deactivateReason || undefined).subscribe(() => {
      this.snack.open('Cuidador desactivado (ripple en curso)', 'Cerrar', { duration: 2500 });
      this.deactivating.set(false);
      this.load();
    });
  }

  reactivate(): void {
    this.api.reactivate(this.id).subscribe(() => {
      this.snack.open('Cuidador reactivado', 'Cerrar', { duration: 2000 });
      this.load();
    });
  }

  back(): void {
    this.router.navigateByUrl('/caregivers');
  }

  dayName(d: number): string {
    return ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'][d] ?? String(d);
  }
}
