import { Routes } from '@angular/router';
import { sessionGuard } from './core/session.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/login/login').then((m) => m.Login),
  },
  {
    path: '',
    loadComponent: () => import('./layout/shell').then((m) => m.Shell),
    canActivate: [sessionGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard').then((m) => m.Dashboard),
      },
      {
        path: 'caregivers',
        loadComponent: () => import('./features/caregivers/queue').then((m) => m.Queue),
      },
      {
        path: 'caregivers/:id',
        loadComponent: () => import('./features/caregivers/detail').then((m) => m.Detail),
      },
      {
        path: 'ranges',
        loadComponent: () => import('./features/ranges/ranges').then((m) => m.Ranges),
      },
      {
        path: 'moderation',
        loadComponent: () => import('./features/moderation/moderation').then((m) => m.Moderation),
      },
      {
        path: 'support',
        loadComponent: () => import('./features/support/support').then((m) => m.Support),
      },
      {
        path: 'audit',
        loadComponent: () => import('./features/audit/audit').then((m) => m.Audit),
      },
    ],
  },
  { path: '**', redirectTo: '' },
];
