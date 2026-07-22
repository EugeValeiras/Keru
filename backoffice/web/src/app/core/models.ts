export interface SessionUser {
  accountId: string;
  email: string;
  role: string;
  displayName?: string;
}

export interface Badges {
  certifications: boolean;
  identity: boolean;
  background: boolean;
}

export interface Certification {
  type: string;
  institution: string;
  year: number;
  verified: boolean;
}

export interface CaregiverCard {
  id: string;
  displayName: string;
  status: 'pending' | 'approved' | 'rejected' | 'deactivated';
  specialties: string[];
  zone: string;
  modalities: string[];
  badges: Badges;
  rejectionReason?: string | null;
}

export interface CaregiverDetail extends CaregiverCard {
  accountId: string;
  certifications: Certification[];
  availability: { dayOfWeek: number; from: string; to: string }[];
  rates: { ratePerHour: number; currency: string; description?: string };
  reviewedBy?: string | null;
  reviewedAt?: string | null;
  createdAt: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface DashboardMetrics {
  caregivers: Record<string, number>;
  requests: Record<string, number>;
  activeAssignments: number;
}

export interface AuditEntry {
  id: string;
  action: string;
  actor: string;
  target?: { type: string; id: string } | null;
  metadata?: Record<string, unknown> | null;
  createdAt: string;
}
