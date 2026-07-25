import { BadRequestException, Injectable } from '@nestjs/common';
import { Manager, AuditUtility, TransactionUtility } from '@keru/core';
import { RangeAccess } from '../resource-access/range.access';
import { MetricRange } from '../resource-access/entities/metric-range.entity';
import { METRIC_DEFINITIONS, METRIC_KEYS } from '../metric-definitions';

export interface PlatformRangeView {
  metricKey: string;
  label: string;
  unit: string;
  min: number;
  max: number;
  version: string;
  source: 'db' | 'catalog';
  plausible: { min: number; max: number };
}

/**
 * RangeManager (constitution §3.1 / NFR-18). Gobierno de rangos: es el "seam" de configuración
 * clínica dentro de CareRecord. Un SetRanges se trata como un evento clínico — con plausibilidad
 * sobre la propia config (NFR-29, versión lite), versión nueva (nunca sobrescribe) y autoría.
 * TODO(NFR-29): confirmación de segundo administrador + rollout gradual.
 * TODO(UC-18): WHO puede setear un override por paciente sigue como gap de negocio.
 */
@Manager()
@Injectable()
export class RangeManager {
  constructor(
    private readonly rangeAccess: RangeAccess,
    private readonly tx: TransactionUtility,
    private readonly audit: AuditUtility,
  ) {}

  /** Rangos de plataforma vigentes (DB o default del catálogo) para todas las métricas. */
  async listPlatformRanges(): Promise<PlatformRangeView[]> {
    const out: PlatformRangeView[] = [];
    for (const metricKey of METRIC_KEYS) {
      const def = METRIC_DEFINITIONS[metricKey];
      const active = await this.rangeAccess.findActive(metricKey, 'platform', null);
      out.push({
        metricKey,
        label: def.label,
        unit: def.unit,
        min: active ? active.min : def.defaultRange.min,
        max: active ? active.max : def.defaultRange.max,
        version: active ? active.version : 'catalog-default',
        source: active ? 'db' : 'catalog',
        plausible: def.plausible,
      });
    }
    return out;
  }

  historyPlatform(metricKey: string): Promise<MetricRange[]> {
    this.assertMetric(metricKey);
    return this.rangeAccess.history(metricKey, 'platform', null);
  }

  /** Set del rango de plataforma (NFR-18). Crea una versión nueva. */
  async setPlatformRange(
    metricKey: string,
    min: number,
    max: number,
    adminId: string,
    adminRole: string,
  ): Promise<MetricRange> {
    const def = this.assertMetric(metricKey);
    this.assertPlausible(metricKey, min, max);

    const range = await this.tx.run((em) =>
      this.rangeAccess.setRange(
        { metricKey, scope: 'platform', patientId: null, min, max, unit: def.unit, createdBy: adminId, createdByRole: adminRole },
        em,
      ),
    );
    await this.audit.record({
      action: 'care-record.range.set',
      actor: adminId,
      target: { type: 'metric_range', id: range.id },
      metadata: { metricKey, scope: 'platform', min, max, version: range.version },
    });
    return range;
  }

  /** Set de override por paciente (NFR-17). Misma disciplina, alcance paciente. */
  async setPatientRange(
    patientId: string,
    metricKey: string,
    min: number,
    max: number,
    adminId: string,
    adminRole: string,
  ): Promise<MetricRange> {
    const def = this.assertMetric(metricKey);
    this.assertPlausible(metricKey, min, max);

    const range = await this.tx.run((em) =>
      this.rangeAccess.setRange(
        { metricKey, scope: 'patient', patientId, min, max, unit: def.unit, createdBy: adminId, createdByRole: adminRole },
        em,
      ),
    );
    await this.audit.record({
      action: 'care-record.range.set',
      actor: adminId,
      target: { type: 'metric_range', id: range.id },
      metadata: { metricKey, scope: 'patient', patientId, min, max, version: range.version },
    });
    return range;
  }

  private assertMetric(metricKey: string) {
    const def = METRIC_DEFINITIONS[metricKey];
    if (!def) throw new BadRequestException(`Métrica desconocida: ${metricKey}`);
    return def;
  }

  /** NFR-29 (lite): bornes de plausibilidad sobre la propia configuración. */
  private assertPlausible(metricKey: string, min: number, max: number): void {
    if (min >= max) throw new BadRequestException('El mínimo debe ser menor que el máximo');
    const p = this.rangeAccess.getPlausible(metricKey);
    if (min < p.min || max > p.max) {
      throw new BadRequestException(
        `El rango debe estar dentro de los bornes de plausibilidad (${p.min}–${p.max} ${p.unit})`,
      );
    }
  }
}
