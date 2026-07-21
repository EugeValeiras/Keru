import { Module } from '@nestjs/common';
import { HiringModule } from '@keru/hiring';
import { ReputationModule } from '@keru/reputation';
import { SchedulerService } from './scheduler.service';
import { OpsController } from './ops.controller';

/** Ops: barrido de vencidos (cron + trigger manual admin). NFR-14. */
@Module({
  imports: [HiringModule, ReputationModule],
  providers: [SchedulerService],
  controllers: [OpsController],
})
export class OpsModule {}
