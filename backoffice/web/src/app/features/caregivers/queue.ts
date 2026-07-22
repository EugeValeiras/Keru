import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../core/api.service';
import { CaregiverCard } from '../../core/models';

@Component({
  selector: 'bo-queue',
  imports: [
    FormsModule,
    MatTableModule,
    MatButtonToggleModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressBarModule,
  ],
  template: `
    <div class="head">
      <h2>Cuidadores</h2>
      <span class="spacer"></span>
      <button mat-stroked-button (click)="runSweep()">
        <mat-icon>cleaning_services</mat-icon> Barrido de vencidos
      </button>
    </div>

    <div class="filters">
      <mat-button-toggle-group [value]="status()" (change)="onFilter($event.value)" hideSingleSelectionIndicator>
        <mat-button-toggle value="pending">Pendientes</mat-button-toggle>
        <mat-button-toggle value="approved">Aprobados</mat-button-toggle>
        <mat-button-toggle value="rejected">Rechazados</mat-button-toggle>
        <mat-button-toggle value="deactivated">Desactivados</mat-button-toggle>
        <mat-button-toggle [value]="''">Todos</mat-button-toggle>
      </mat-button-toggle-group>
      <mat-form-field appearance="outline" class="search" subscriptSizing="dynamic">
        <mat-icon matPrefix>search</mat-icon>
        <mat-label>Buscar por nombre o zona</mat-label>
        <input matInput [(ngModel)]="q" (keyup.enter)="load()" />
      </mat-form-field>
    </div>

    @if (loading()) {
      <mat-progress-bar mode="indeterminate" />
    }

    <table mat-table [dataSource]="rows()" class="mat-elevation-z1 tbl">
      <ng-container matColumnDef="name">
        <th mat-header-cell *matHeaderCellDef>Cuidador</th>
        <td mat-cell *matCellDef="let c">{{ c.displayName }}</td>
      </ng-container>
      <ng-container matColumnDef="specialties">
        <th mat-header-cell *matHeaderCellDef>Especialidades</th>
        <td mat-cell *matCellDef="let c">
          <mat-chip-set>
            @for (s of c.specialties; track s) { <mat-chip>{{ s }}</mat-chip> }
          </mat-chip-set>
        </td>
      </ng-container>
      <ng-container matColumnDef="zone">
        <th mat-header-cell *matHeaderCellDef>Zona</th>
        <td mat-cell *matCellDef="let c">{{ c.zone }}</td>
      </ng-container>
      <ng-container matColumnDef="status">
        <th mat-header-cell *matHeaderCellDef>Estado</th>
        <td mat-cell *matCellDef="let c">
          <span class="badge" [class]="c.status">{{ c.status }}</span>
        </td>
      </ng-container>
      <ng-container matColumnDef="actions">
        <th mat-header-cell *matHeaderCellDef></th>
        <td mat-cell *matCellDef="let c">
          <button mat-button color="primary" (click)="open(c)">Revisar</button>
        </td>
      </ng-container>
      <tr mat-header-row *matHeaderRowDef="cols"></tr>
      <tr mat-row *matRowDef="let row; columns: cols"></tr>
    </table>

    @if (!loading() && rows().length === 0) {
      <p class="empty">No hay cuidadores en este estado.</p>
    }
  `,
  styles: [
    `
      .head {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .spacer {
        flex: 1 1 auto;
      }
      .filters {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 8px 0 16px;
        flex-wrap: wrap;
      }
      .search {
        min-width: 280px;
      }
      .tbl {
        width: 100%;
        background: #fff;
      }
      .empty {
        color: #777;
        margin-top: 24px;
      }
      .badge {
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        text-transform: capitalize;
      }
      .badge.pending {
        background: #fff4d6;
        color: #8a6100;
      }
      .badge.approved {
        background: #d6f5df;
        color: #1b6b3a;
      }
      .badge.rejected {
        background: #fbdcdc;
        color: #9b2222;
      }
      .badge.deactivated {
        background: #e0e0e0;
        color: #555;
      }
    `,
  ],
})
export class Queue {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  private readonly snack = inject(MatSnackBar);

  readonly cols = ['name', 'specialties', 'zone', 'status', 'actions'];
  readonly rows = signal<CaregiverCard[]>([]);
  readonly loading = signal(false);
  readonly status = signal<string>('pending');
  q = '';

  constructor() {
    this.load();
  }

  onFilter(value: string): void {
    this.status.set(value);
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.api.listCaregivers(this.status() || undefined, this.q || undefined).subscribe({
      next: (p) => this.rows.set(p.items),
      error: () => this.snack.open('Error cargando cuidadores', 'Cerrar', { duration: 3000 }),
      complete: () => this.loading.set(false),
    });
  }

  open(c: CaregiverCard): void {
    this.router.navigate(['/caregivers', c.id]);
  }

  runSweep(): void {
    this.api.sweep().subscribe((r) =>
      this.snack.open(
        `Barrido: ${r.assignmentsClosed} asignaciones, ${r.requestsExpired} solicitudes, ${r.revealed} reseñas`,
        'Cerrar',
        { duration: 4000 },
      ),
    );
  }
}
