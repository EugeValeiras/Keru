import { Injectable, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { EntityManager, IsNull, Repository } from 'typeorm';
import { ResourceAccess } from '@keru/core';
import { METRIC_DEFINITIONS } from '../metric-definitions';
import { MetricRange, RangeScope } from './entities/metric-range.entity';

export interface ApplicableRange {
  metricKey: string;
  min: number;
  max: number;
  unit: string;
  version: string;
}

export interface SetRangeInput {
  metricKey: string;
  scope: RangeScope;
  patientId: string | null;
  min: number;
  max: number;
  unit: string;
  createdBy: string;
  createdByRole: string;
}

/**
 * RangeAccess (constitution §3.1). Rangos como datos versionados (NFR-17/28). Resolución del rango
 * aplicable: override por paciente -> default de plataforma (DB) -> default del catálogo (fallback).
 * Los bornes de plausibilidad viven en el catálogo (NFR-16). Nunca se sobrescribe: cada cambio es
 * una versión nueva y la anterior queda inactiva (historial).
 */
@ResourceAccess()
@Injectable()
export class RangeAccess {
  constructor(@InjectRepository(MetricRange) private readonly ranges: Repository<MetricRange>) {}

  /** Rango aplicable (NFR-17): paciente -> plataforma -> catálogo. */
  async getApplicableRange(metricKey: string, patientId?: string): Promise<ApplicableRange> {
    if (patientId) {
      const override = await this.findActive(metricKey, 'patient', patientId);
      if (override) return this.toApplicable(override);
    }
    const platform = await this.findActive(metricKey, 'platform', null);
    if (platform) return this.toApplicable(platform);

    const def = this.def(metricKey);
    return { metricKey, min: def.defaultRange.min, max: def.defaultRange.max, unit: def.unit, version: 'catalog-default' };
  }

  getPlausible(metricKey: string): { min: number; max: number; unit: string } {
    const def = this.def(metricKey);
    return { ...def.plausible, unit: def.unit };
  }

  findActive(metricKey: string, scope: RangeScope, patientId: string | null): Promise<MetricRange | null> {
    return this.ranges.findOne({
      where: { metricKey, scope, patientId: patientId ?? IsNull(), active: true },
    });
  }

  /** Todas las plataformas activas (para el listado admin). */
  listActivePlatform(): Promise<MetricRange[]> {
    return this.ranges.find({ where: { scope: 'platform', active: true } });
  }

  /** Historial completo de versiones de una clave (NFR-28). */
  history(metricKey: string, scope: RangeScope, patientId: string | null): Promise<MetricRange[]> {
    return this.ranges.find({
      where: { metricKey, scope, patientId: patientId ?? IsNull() },
      order: { createdAt: 'DESC' },
    });
  }

  /** Crea una versión nueva (desactiva la anterior). Transaccional: recibe el EntityManager. */
  async setRange(input: SetRangeInput, manager: EntityManager): Promise<MetricRange> {
    const repo = manager.getRepository(MetricRange);
    const now = new Date();

    // Desactivar la versión activa anterior (nunca se borra).
    await repo.update(
      { metricKey: input.metricKey, scope: input.scope, patientId: input.patientId ?? IsNull(), active: true },
      { active: false, supersededAt: now },
    );

    const count = await repo.count({
      where: { metricKey: input.metricKey, scope: input.scope, patientId: input.patientId ?? IsNull() },
    });
    const version = `${input.scope}-v${count + 1}`;

    return repo.save(
      repo.create({
        metricKey: input.metricKey,
        scope: input.scope,
        patientId: input.patientId,
        min: input.min,
        max: input.max,
        unit: input.unit,
        version,
        active: true,
        createdBy: input.createdBy,
        createdByRole: input.createdByRole,
        effectiveFrom: now,
      }),
    );
  }

  private toApplicable(r: MetricRange): ApplicableRange {
    return { metricKey: r.metricKey, min: r.min, max: r.max, unit: r.unit, version: r.version };
  }

  private def(metricKey: string) {
    const def = METRIC_DEFINITIONS[metricKey];
    if (!def) throw new BadRequestException(`Métrica desconocida: ${metricKey}`);
    return def;
  }
}
