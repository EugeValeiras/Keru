import { Component, inject, signal } from '@angular/core';
import { DatePipe, JsonPipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { ApiService } from '../../core/api.service';
import { AuditEntry } from '../../core/models';

@Component({
  selector: 'bo-audit',
  imports: [DatePipe, JsonPipe, MatTableModule, MatProgressBarModule],
  template: `
    <h2>Auditoría</h2>
    @if (loading()) { <mat-progress-bar mode="indeterminate" /> }
    <table mat-table [dataSource]="rows()" class="mat-elevation-z1 tbl">
      <ng-container matColumnDef="createdAt">
        <th mat-header-cell *matHeaderCellDef>Fecha</th>
        <td mat-cell *matCellDef="let e">{{ e.createdAt | date: 'short' }}</td>
      </ng-container>
      <ng-container matColumnDef="action">
        <th mat-header-cell *matHeaderCellDef>Acción</th>
        <td mat-cell *matCellDef="let e"><code>{{ e.action }}</code></td>
      </ng-container>
      <ng-container matColumnDef="actor">
        <th mat-header-cell *matHeaderCellDef>Actor</th>
        <td mat-cell *matCellDef="let e">{{ e.actor }}</td>
      </ng-container>
      <ng-container matColumnDef="target">
        <th mat-header-cell *matHeaderCellDef>Objeto</th>
        <td mat-cell *matCellDef="let e">{{ e.target | json }}</td>
      </ng-container>
      <tr mat-header-row *matHeaderRowDef="cols"></tr>
      <tr mat-row *matRowDef="let row; columns: cols"></tr>
    </table>
  `,
  styles: [
    `
      .tbl { width: 100%; background: #fff; margin-top: 12px; }
      code { font-size: 12px; }
    `,
  ],
})
export class Audit {
  private readonly api = inject(ApiService);
  readonly cols = ['createdAt', 'action', 'actor', 'target'];
  readonly rows = signal<AuditEntry[]>([]);
  readonly loading = signal(false);

  constructor() {
    this.loading.set(true);
    this.api.audit(1, 50).subscribe({
      next: (p) => this.rows.set(p.items),
      complete: () => this.loading.set(false),
    });
  }
}
