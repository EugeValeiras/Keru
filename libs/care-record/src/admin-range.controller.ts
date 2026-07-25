import { Body, Controller, Get, Param, Put, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOkResponse, ApiOperation, ApiTags } from '@nestjs/swagger';
import { AuthPrincipal, CurrentAccount, JwtAuthGuard, Roles, RolesGuard } from '@keru/core';
import { RangeManager } from './manager/range.manager';
import { SetRangeDto } from './manager/dto/set-range.dto';

/** UC-18/NFR-18 · Gobierno de rangos clínicos (back-office). Requiere rol admin. */
@ApiTags('Ranges')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Controller('admin')
export class AdminRangeController {
  constructor(private readonly ranges: RangeManager) {}

  @Get('ranges')
  @ApiOperation({ summary: 'Rangos de plataforma vigentes (con plausibilidad y versión)' })
  @ApiOkResponse({ description: 'Lista de rangos por métrica' })
  listRanges() {
    return this.ranges.listPlatformRanges();
  }

  @Get('ranges/:metricKey/history')
  @ApiOperation({ summary: 'NFR-28 · Historial de versiones de un rango de plataforma' })
  history(@Param('metricKey') metricKey: string) {
    return this.ranges.historyPlatform(metricKey);
  }

  @Put('ranges/:metricKey')
  @ApiOperation({ summary: 'NFR-18 · Setear el rango de plataforma (crea una versión nueva)' })
  setPlatformRange(
    @Param('metricKey') metricKey: string,
    @Body() dto: SetRangeDto,
    @CurrentAccount() admin: AuthPrincipal,
  ) {
    return this.ranges.setPlatformRange(metricKey, dto.min, dto.max, admin.accountId, admin.role);
  }

  @Put('patients/:patientId/ranges/:metricKey')
  @ApiOperation({ summary: 'NFR-17 · Setear override de rango por paciente' })
  setPatientRange(
    @Param('patientId') patientId: string,
    @Param('metricKey') metricKey: string,
    @Body() dto: SetRangeDto,
    @CurrentAccount() admin: AuthPrincipal,
  ) {
    return this.ranges.setPatientRange(patientId, metricKey, dto.min, dto.max, admin.accountId, admin.role);
  }
}
