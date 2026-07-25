import { Column, CreateDateColumn, Entity, Index, PrimaryGeneratedColumn } from 'typeorm';

export type RangeScope = 'platform' | 'patient';

/**
 * Rango de una métrica (NFR-17/28). Efectivo-fechado y **nunca sobrescrito**: cada cambio crea una
 * versión nueva y desactiva la anterior (queda como historial). Dos alcances: `platform` (default) y
 * `patient` (override). Autoría con rol (NFR-18: un SetRanges es como un evento clínico).
 */
@Entity({ name: 'metric_range' })
export class MetricRange {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ type: 'varchar', length: 64 })
  @Index()
  metricKey!: string;

  @Column({ type: 'varchar', length: 16 })
  scope!: RangeScope;

  /** null para platform; el paciente para override. */
  @Column({ type: 'uuid', nullable: true })
  @Index()
  patientId!: string | null;

  @Column({ type: 'double precision' })
  min!: number;

  @Column({ type: 'double precision' })
  max!: number;

  @Column({ type: 'varchar', length: 16 })
  unit!: string;

  /** p. ej. platform-v2 / patient-v1. */
  @Column({ type: 'varchar', length: 32 })
  version!: string;

  /** Versión vigente (solo una activa por metricKey+scope+patientId). */
  @Column({ type: 'boolean', default: true })
  @Index()
  active!: boolean;

  /** Autoría (NFR-18). */
  @Column({ type: 'varchar', length: 128 })
  createdBy!: string;

  @Column({ type: 'varchar', length: 32 })
  createdByRole!: string;

  @Column({ type: 'timestamptz' })
  effectiveFrom!: Date;

  @Column({ type: 'timestamptz', nullable: true })
  supersededAt!: Date | null;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt!: Date;
}
