import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService } from '../../core/api.service';
import { PlatformRange, RangeVersion } from '../../core/models';

@Component({
  selector: 'bo-ranges',
  imports: [
    DatePipe,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressBarModule,
  ],
  template: `
    <h2>Rangos clínicos</h2>
    <p class="muted">
      Rango de referencia por métrica. Al guardar se crea una versión nueva (la anterior queda como
      historial, nunca se sobrescribe). El valor debe estar dentro de los bornes de plausibilidad.
    </p>
    @if (loading()) { <mat-progress-bar mode="indeterminate" /> }

    <table mat-table [dataSource]="rows()" class="mat-elevation-z1 tbl">
      <ng-container matColumnDef="metric">
        <th mat-header-cell *matHeaderCellDef>Métrica</th>
        <td mat-cell *matCellDef="let r">
          <b>{{ r.label }}</b> <span class="unit">{{ r.unit }}</span>
        </td>
      </ng-container>
      <ng-container matColumnDef="plausible">
        <th mat-header-cell *matHeaderCellDef>Plausible</th>
        <td mat-cell *matCellDef="let r" class="muted">{{ r.plausible.min }}–{{ r.plausible.max }}</td>
      </ng-container>
      <ng-container matColumnDef="range">
        <th mat-header-cell *matHeaderCellDef>Rango de referencia</th>
        <td mat-cell *matCellDef="let r">
          <input class="num" type="number" [(ngModel)]="r.min" />
          <span>–</span>
          <input class="num" type="number" [(ngModel)]="r.max" />
        </td>
      </ng-container>
      <ng-container matColumnDef="version">
        <th mat-header-cell *matHeaderCellDef>Versión</th>
        <td mat-cell *matCellDef="let r">
          <span class="ver" [class.catalog]="r.source === 'catalog'">{{ r.version }}</span>
        </td>
      </ng-container>
      <ng-container matColumnDef="actions">
        <th mat-header-cell *matHeaderCellDef></th>
        <td mat-cell *matCellDef="let r">
          <button mat-flat-button color="primary" (click)="save(r)">Guardar</button>
          <button mat-button (click)="showHistory(r.metricKey)">Historial</button>
        </td>
      </ng-container>
      <tr mat-header-row *matHeaderRowDef="cols"></tr>
      <tr mat-row *matRowDef="let row; columns: cols"></tr>
    </table>

    @if (historyMetric()) {
      <mat-card class="hist">
        <mat-card-header>
          <mat-card-title>Historial · {{ historyMetric() }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          @for (v of history(); track v.id) {
            <div class="hrow">
              <span class="ver" [class.active]="v.active">{{ v.version }}</span>
              <span>{{ v.min }}–{{ v.max }}</span>
              <span class="muted">{{ v.effectiveFrom | date: 'short' }} · por {{ v.createdBy }} ({{ v.createdByRole }})</span>
              @if (v.active) { <span class="tag">activa</span> }
            </div>
          }
          <button mat-button (click)="historyMetric.set(null)">Cerrar</button>
        </mat-card-content>
      </mat-card>
    }
  `,
  styles: [
    `
      .muted { color: #777; }
      .tbl { width: 100%; background: #fff; margin-top: 12px; }
      .unit { color: #999; margin-left: 6px; font-size: 12px; }
      .num { width: 70px; padding: 6px; border: 1px solid #ccc; border-radius: 6px; }
      .ver { font-size: 12px; background: #e6f0ff; color: #1256a0; padding: 2px 8px; border-radius: 10px; }
      .ver.catalog { background: #eee; color: #777; }
      .ver.active { background: #d6f5df; color: #1b6b3a; }
      .hist { margin-top: 16px; }
      .hrow { display: flex; align-items: center; gap: 12px; padding: 6px 0; }
      .tag { background: #d6f5df; color: #1b6b3a; border-radius: 10px; padding: 2px 8px; font-size: 12px; }
    `,
  ],
})
export class Ranges {
  private readonly api = inject(ApiService);
  private readonly snack = inject(MatSnackBar);

  readonly cols = ['metric', 'plausible', 'range', 'version', 'actions'];
  readonly rows = signal<PlatformRange[]>([]);
  readonly loading = signal(false);
  readonly historyMetric = signal<string | null>(null);
  readonly history = signal<RangeVersion[]>([]);

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.api.ranges().subscribe({
      next: (r) => this.rows.set(r),
      complete: () => this.loading.set(false),
    });
  }

  save(r: PlatformRange): void {
    this.api.setRange(r.metricKey, Number(r.min), Number(r.max)).subscribe({
      next: () => {
        this.snack.open('Rango actualizado (nueva versión)', 'Cerrar', { duration: 2000 });
        this.load();
        if (this.historyMetric() === r.metricKey) this.showHistory(r.metricKey);
      },
      error: (e: HttpErrorResponse) =>
        this.snack.open(e.error?.message ?? 'Error al guardar el rango', 'Cerrar', { duration: 4000 }),
    });
  }

  showHistory(metricKey: string): void {
    this.historyMetric.set(metricKey);
    this.api.rangeHistory(metricKey).subscribe((h) => this.history.set(h));
  }
}
