import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../core/api.service';
import { ModeratedReview } from '../../core/models';

@Component({
  selector: 'bo-moderation',
  imports: [DatePipe, MatTableModule, MatButtonModule, MatIconModule, MatProgressBarModule],
  template: `
    <h2>Moderación de reseñas</h2>
    <p class="muted">Retener oculta la reseña del público y de los promedios, pero preserva el original.</p>
    @if (loading()) { <mat-progress-bar mode="indeterminate" /> }

    <table mat-table [dataSource]="rows()" class="mat-elevation-z1 tbl">
      <ng-container matColumnDef="subject">
        <th mat-header-cell *matHeaderCellDef>Sujeto</th>
        <td mat-cell *matCellDef="let r">{{ r.subjectType === 'caregiver' ? 'Cuidador' : 'Paciente' }}</td>
      </ng-container>
      <ng-container matColumnDef="rating">
        <th mat-header-cell *matHeaderCellDef>Puntaje</th>
        <td mat-cell *matCellDef="let r">{{ r.rating }} ★</td>
      </ng-container>
      <ng-container matColumnDef="comment">
        <th mat-header-cell *matHeaderCellDef>Comentario</th>
        <td mat-cell *matCellDef="let r">{{ r.comment || '—' }}</td>
      </ng-container>
      <ng-container matColumnDef="date">
        <th mat-header-cell *matHeaderCellDef>Fecha</th>
        <td mat-cell *matCellDef="let r" class="muted">{{ r.createdAt | date: 'short' }}</td>
      </ng-container>
      <ng-container matColumnDef="visibility">
        <th mat-header-cell *matHeaderCellDef>Estado</th>
        <td mat-cell *matCellDef="let r">
          <span class="badge" [class.withheld]="r.visibility === 'withheld'">
            {{ r.visibility === 'withheld' ? 'retenida' : 'publicada' }}
          </span>
        </td>
      </ng-container>
      <ng-container matColumnDef="actions">
        <th mat-header-cell *matHeaderCellDef></th>
        <td mat-cell *matCellDef="let r">
          @if (r.visibility === 'published') {
            <button mat-stroked-button color="warn" (click)="withhold(r)">
              <mat-icon>visibility_off</mat-icon> Retener
            </button>
          } @else {
            <button mat-stroked-button color="primary" (click)="publish(r)">
              <mat-icon>visibility</mat-icon> Republicar
            </button>
          }
        </td>
      </ng-container>
      <tr mat-header-row *matHeaderRowDef="cols"></tr>
      <tr mat-row *matRowDef="let row; columns: cols"></tr>
    </table>
    @if (!loading() && rows().length === 0) { <p class="muted">No hay reseñas para moderar.</p> }
  `,
  styles: [
    `
      .muted { color: #777; }
      .tbl { width: 100%; background: #fff; margin-top: 12px; }
      .badge { padding: 2px 10px; border-radius: 12px; font-size: 12px; background: #d6f5df; color: #1b6b3a; }
      .badge.withheld { background: #fbdcdc; color: #9b2222; }
    `,
  ],
})
export class Moderation {
  private readonly api = inject(ApiService);
  private readonly snack = inject(MatSnackBar);

  readonly cols = ['subject', 'rating', 'comment', 'date', 'visibility', 'actions'];
  readonly rows = signal<ModeratedReview[]>([]);
  readonly loading = signal(false);

  constructor() {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.api.reviewsForModeration().subscribe({
      next: (p) => this.rows.set(p.items),
      complete: () => this.loading.set(false),
    });
  }

  withhold(r: ModeratedReview): void {
    this.api.withholdReview(r.id).subscribe(() => {
      this.snack.open('Reseña retenida', 'Cerrar', { duration: 2000 });
      this.load();
    });
  }

  publish(r: ModeratedReview): void {
    this.api.publishReview(r.id).subscribe(() => {
      this.snack.open('Reseña republicada', 'Cerrar', { duration: 2000 });
      this.load();
    });
  }
}
