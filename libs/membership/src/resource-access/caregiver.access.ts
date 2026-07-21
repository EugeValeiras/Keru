import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ResourceAccess } from '@keru/core';
import {
  AvailabilitySlot,
  Caregiver,
  CaregiverStatus,
  Certification,
  Rates,
  VerificationBadges,
} from './entities/caregiver.entity';

export interface CreateCaregiverInput {
  accountId: string;
  displayName: string;
  specialties: string[];
  certifications: Certification[];
  availability: AvailabilitySlot[];
  rates: Rates;
  zone: string;
  modalities: string[];
}

/**
 * CaregiverAccess (constitution §3.1). Verbos atómicos sobre el perfil de cuidador: personas +
 * cuentas, perfiles, tarifas efectivo-fechadas, insignias + provenance, ciclo de aprobación,
 * visibilidad. Verbos mutantes idempotentes (NFR-34). Dueño: Membership.
 */
@ResourceAccess()
@Injectable()
export class CaregiverAccess {
  constructor(@InjectRepository(Caregiver) private readonly caregivers: Repository<Caregiver>) {}

  /** UC-02. Idempotente por operationId; un perfil por cuenta. Las certificaciones nacen no verificadas. */
  async createProfile(input: CreateCaregiverInput, operationId: string): Promise<Caregiver> {
    const existing = await this.caregivers.findOne({ where: { createdByOperationId: operationId } });
    if (existing) return existing;

    const caregiver = this.caregivers.create({
      ...input,
      certifications: input.certifications.map((c) => ({ ...c, verified: false })),
      status: 'pending',
      badges: { certifications: false, identity: false, background: false },
      createdByOperationId: operationId,
    });
    return this.caregivers.save(caregiver);
  }

  findById(id: string): Promise<Caregiver | null> {
    return this.caregivers.findOne({ where: { id } });
  }

  findByAccountId(accountId: string): Promise<Caregiver | null> {
    return this.caregivers.findOne({ where: { accountId } });
  }

  listByStatus(status: CaregiverStatus): Promise<Caregiver[]> {
    return this.caregivers.find({ where: { status }, order: { createdAt: 'ASC' } });
  }

  /** UC-19. Transición de estado con provenance (quién/cuándo). */
  async setStatus(
    id: string,
    status: CaregiverStatus,
    reviewedBy: string,
    rejectionReason: string | null,
    reviewedAt: Date,
  ): Promise<void> {
    await this.caregivers.update(id, { status, reviewedBy, reviewedAt, rejectionReason });
  }

  /** UC-19. Actualiza las insignias de verificación (los tres niveles son independientes). */
  async setBadges(id: string, badges: VerificationBadges): Promise<void> {
    await this.caregivers.update(id, { badges });
  }
}
