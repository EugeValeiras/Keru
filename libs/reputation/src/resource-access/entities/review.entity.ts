import { Column, CreateDateColumn, Entity, Index, PrimaryGeneratedColumn, Unique } from 'typeorm';

export type ReviewSubject = 'caregiver' | 'patient';

/**
 * Reseña bidireccional (UC-17/21). Una por servicio y por autor (I5, inmutable). Sellada hasta que
 * ambas partes envían o cierra la ventana (reveal simultáneo, NFR-21). Solo con servicio finalizado.
 */
@Entity({ name: 'review' })
@Unique(['requestId', 'authorAccountId'])
export class Review {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ type: 'uuid' })
  @Index()
  requestId!: string;

  @Column({ type: 'varchar', length: 128 })
  authorAccountId!: string;

  @Column({ type: 'varchar', length: 16 })
  subjectType!: ReviewSubject;

  @Column({ type: 'uuid' })
  @Index()
  subjectId!: string;

  @Column({ type: 'int' })
  rating!: number; // 1..5

  @Column({ type: 'varchar', length: 1000, nullable: true })
  comment!: string | null;

  /** Sellada hasta el reveal simultáneo (NFR-21). */
  @Column({ type: 'boolean', default: false })
  @Index()
  revealed!: boolean;

  /**
   * Visibilidad (NFR-22). `withheld` = retenida por moderación: se oculta del público y de los
   * agregados, PERO el contenido original se preserva (nunca se borra).
   */
  @Column({ type: 'varchar', length: 16, default: 'published' })
  visibility!: 'published' | 'withheld';

  @Column({ type: 'varchar', length: 128, nullable: true })
  moderatedBy!: string | null;

  @Column({ type: 'timestamptz', nullable: true })
  moderatedAt!: Date | null;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt!: Date;
}
