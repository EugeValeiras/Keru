import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOkResponse, ApiOperation, ApiQuery, ApiTags } from '@nestjs/swagger';
import { JwtAuthGuard, Roles, RolesGuard } from '@keru/core';
import { MembershipManager } from './manager/membership.manager';

/** Soporte de pacientes (back-office). Requiere rol admin. */
@ApiTags('Support')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Controller('admin/patients')
export class AdminPatientController {
  constructor(private readonly membership: MembershipManager) {}

  @Get()
  @ApiOperation({ summary: 'Buscar pacientes por nombre (paginado)' })
  @ApiQuery({ name: 'q', required: false })
  @ApiQuery({ name: 'page', required: false, type: Number })
  @ApiQuery({ name: 'pageSize', required: false, type: Number })
  @ApiOkResponse({ description: 'Página de pacientes' })
  async search(@Query('q') q?: string, @Query('page') page = '1', @Query('pageSize') pageSize = '20') {
    const r = await this.membership.searchPatients(q, Number(page), Number(pageSize));
    return {
      ...r,
      items: r.items.map((p) => ({
        id: p.patient.id,
        fullName: p.patient.fullName,
        age: p.age,
        mainCondition: p.patient.mainCondition,
      })),
    };
  }
}
