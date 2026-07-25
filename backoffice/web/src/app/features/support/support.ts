import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService } from '../../core/api.service';
import { CaregiverCard, PatientCard } from '../../core/models';

@Component({
  selector: 'bo-support',
  imports: [
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
  ],
  template: `
    <h2>Soporte</h2>
    <div class="grid">
      <mat-card>
        <mat-card-header><mat-card-title>Buscar paciente</mat-card-title></mat-card-header>
        <mat-card-content>
          <mat-form-field appearance="outline" class="full">
            <mat-icon matPrefix>search</mat-icon>
            <mat-label>Nombre del paciente</mat-label>
            <input matInput [(ngModel)]="q" (keyup.enter)="searchPatients()" />
          </mat-form-field>
          <mat-nav-list>
            @for (p of patients(); track p.id) {
              <a mat-list-item (click)="selectPatient(p)">
                <span matListItemTitle>{{ p.fullName }}</span>
                <span matListItemLine>{{ p.age }} años · {{ p.mainCondition }}</span>
              </a>
            }
          </mat-nav-list>
        </mat-card-content>
      </mat-card>

      <mat-card>
        <mat-card-header>
          <mat-card-title>Asignación manual (UC-05)</mat-card-title>
          <mat-card-subtitle>Caso especial / soporte. Queda auditada.</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <div class="selected">
            Paciente: <b>{{ selected()?.fullName ?? '— elegí uno de la lista —' }}</b>
          </div>
          <mat-form-field appearance="outline" class="full">
            <mat-label>Cuidador (aprobado)</mat-label>
            <mat-select [(ngModel)]="caregiverId">
              @for (c of caregivers(); track c.id) {
                <mat-option [value]="c.id">{{ c.displayName }} — {{ c.zone }}</mat-option>
              }
            </mat-select>
          </mat-form-field>
          <div class="dates">
            <mat-form-field appearance="outline">
              <mat-label>Desde</mat-label>
              <input matInput type="date" [(ngModel)]="startDate" />
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>Hasta</mat-label>
              <input matInput type="date" [(ngModel)]="endDate" />
            </mat-form-field>
          </div>
          <button
            mat-flat-button
            color="primary"
            [disabled]="!selected() || !caregiverId || !startDate || !endDate"
            (click)="assign()"
          >
            <mat-icon>assignment_ind</mat-icon> Crear asignación
          </button>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 12px; }
      @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
      .full { width: 100%; }
      .dates { display: flex; gap: 12px; }
      .selected { margin-bottom: 12px; }
    `,
  ],
})
export class Support {
  private readonly api = inject(ApiService);
  private readonly snack = inject(MatSnackBar);

  q = '';
  caregiverId = '';
  startDate = '';
  endDate = '';
  readonly patients = signal<PatientCard[]>([]);
  readonly caregivers = signal<CaregiverCard[]>([]);
  readonly selected = signal<PatientCard | null>(null);

  constructor() {
    this.searchPatients();
    this.api.listCaregivers('approved').subscribe((p) => this.caregivers.set(p.items));
  }

  searchPatients(): void {
    this.api.searchPatients(this.q || undefined).subscribe((p) => this.patients.set(p.items));
  }

  selectPatient(p: PatientCard): void {
    this.selected.set(p);
  }

  assign(): void {
    const p = this.selected();
    if (!p) return;
    this.api
      .manualAssign(this.caregiverId, p.id, new Date(this.startDate).toISOString(), new Date(this.endDate).toISOString())
      .subscribe({
        next: () => {
          this.snack.open('Asignación creada', 'Cerrar', { duration: 2500 });
          this.caregiverId = '';
          this.startDate = '';
          this.endDate = '';
        },
        error: (e: HttpErrorResponse) =>
          this.snack.open(e.error?.message ?? 'No se pudo crear la asignación', 'Cerrar', { duration: 4000 }),
      });
  }
}
