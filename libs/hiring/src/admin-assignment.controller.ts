import { Body, Controller, Post, UseGuards } from '@nestjs/common';
import { IsDateString, IsUUID } from 'class-validator';
import { ApiBearerAuth, ApiCreatedResponse, ApiOperation, ApiProperty, ApiTags } from '@nestjs/swagger';
import { AuthPrincipal, CurrentAccount, JwtAuthGuard, Roles, RolesGuard } from '@keru/core';
import { HiringManager } from './manager/hiring.manager';

class ManualAssignDto {
  @ApiProperty({ format: 'uuid' })
  @IsUUID()
  caregiverId!: string;

  @ApiProperty({ format: 'uuid' })
  @IsUUID()
  patientId!: string;

  @ApiProperty({ example: '2026-08-01T08:00:00Z' })
  @IsDateString()
  startDate!: string;

  @ApiProperty({ example: '2026-08-31T18:00:00Z' })
  @IsDateString()
  endDate!: string;
}

/** UC-05/NFR-40 · Asignación manual (soporte). Requiere rol admin. */
@ApiTags('Support')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Controller('admin/assignments')
export class AdminAssignmentController {
  constructor(private readonly hiring: HiringManager) {}

  @Post()
  @ApiOperation({ summary: 'UC-05/NFR-40 · Crear asignación manual (auditada, provenance=manual)' })
  @ApiCreatedResponse({ description: 'Asignación creada' })
  async assign(@Body() dto: ManualAssignDto, @CurrentAccount() admin: AuthPrincipal) {
    const a = await this.hiring.manualAssign(
      dto.caregiverId,
      dto.patientId,
      new Date(dto.startDate),
      new Date(dto.endDate),
      admin.accountId,
    );
    return { id: a.id, caregiverId: a.caregiverId, patientId: a.patientId, status: a.status, provenance: a.provenance };
  }
}
