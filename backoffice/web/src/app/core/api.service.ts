import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuditEntry, Badges, CaregiverCard, CaregiverDetail, DashboardMetrics, Page } from './models';

/** Cliente del back-office contra el BFF (`/bff/api/*` -> Keru API). */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = '/bff/api';

  // --- Cuidadores (UC-19) ---
  pendingCaregivers(): Observable<CaregiverCard[]> {
    return this.http.get<CaregiverCard[]>(`${this.base}/admin/caregivers/pending`);
  }

  listCaregivers(status?: string, q?: string, page = 1, pageSize = 50): Observable<Page<CaregiverCard>> {
    let params = new HttpParams().set('page', page).set('pageSize', pageSize);
    if (status) params = params.set('status', status);
    if (q) params = params.set('q', q);
    return this.http.get<Page<CaregiverCard>>(`${this.base}/admin/caregivers`, { params });
  }

  dashboard(): Observable<DashboardMetrics> {
    return this.http.get<DashboardMetrics>(`${this.base}/admin/dashboard`);
  }

  caregiver(id: string): Observable<CaregiverDetail> {
    return this.http.get<CaregiverDetail>(`${this.base}/admin/caregivers/${id}`);
  }

  approve(id: string): Observable<CaregiverCard> {
    return this.http.post<CaregiverCard>(`${this.base}/admin/caregivers/${id}/approve`, {});
  }

  reject(id: string, reason: string): Observable<CaregiverCard> {
    return this.http.post<CaregiverCard>(`${this.base}/admin/caregivers/${id}/reject`, { reason });
  }

  setBadges(id: string, badges: Partial<Badges>): Observable<CaregiverCard> {
    return this.http.put<CaregiverCard>(`${this.base}/admin/caregivers/${id}/badges`, badges);
  }

  deactivate(id: string, reason?: string): Observable<CaregiverCard> {
    return this.http.post<CaregiverCard>(`${this.base}/admin/caregivers/${id}/deactivate`, { reason });
  }

  reactivate(id: string): Observable<CaregiverCard> {
    return this.http.post<CaregiverCard>(`${this.base}/admin/caregivers/${id}/reactivate`, {});
  }

  // --- Auditoría / ops ---
  audit(page = 1, pageSize = 20): Observable<Page<AuditEntry>> {
    const params = new HttpParams().set('page', page).set('pageSize', pageSize);
    return this.http.get<Page<AuditEntry>>(`${this.base}/admin/audit`, { params });
  }

  sweep(): Observable<{ assignmentsClosed: number; requestsExpired: number; revealed: number }> {
    return this.http.post<{ assignmentsClosed: number; requestsExpired: number; revealed: number }>(
      `${this.base}/admin/ops/sweep`,
      {},
    );
  }
}
