import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { EntityManager, Repository } from 'typeorm';
import { AuditLog } from './audit-log.entity';

export interface AuditRecord {
  action: string;
  actor: string;
  target?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  /** Si se pasa, la traza se escribe dentro de esa transacción (atómica con el cambio). */
  manager?: EntityManager;
}

/** AuditUtility: punto único para registrar trazas auditables (constitution §5, NFR-33). */
@Injectable()
export class AuditUtility {
  constructor(
    @InjectRepository(AuditLog) private readonly repo: Repository<AuditLog>,
  ) {}

  async record(entry: AuditRecord): Promise<void> {
    const repo = entry.manager ? entry.manager.getRepository(AuditLog) : this.repo;
    await repo.save(
      repo.create({
        action: entry.action,
        actor: entry.actor,
        target: entry.target ?? null,
        metadata: entry.metadata ?? null,
      }),
    );
  }
}
