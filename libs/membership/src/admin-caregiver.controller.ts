import { Body, Controller, Get, Param, Post, Put, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOkResponse, ApiOperation, ApiTags } from '@nestjs/swagger';
import { AuthPrincipal, CurrentAccount, JwtAuthGuard, Roles, RolesGuard } from '@keru/core';
import { MembershipManager } from './manager/membership.manager';
import { CaregiverResponseDto } from './manager/dto/caregiver-response.dto';
import { RejectCaregiverDto, SetBadgesDto } from './manager/dto/admin-caregiver.dto';

/** UC-19 · Back-office: aprobación y verificación de cuidadores. Requiere rol `admin`. */
@ApiTags('Back-office')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Controller('admin/caregivers')
export class AdminCaregiverController {
  constructor(private readonly membership: MembershipManager) {}

  @Get('pending')
  @ApiOperation({ summary: 'UC-19 · Cola de cuidadores pendientes de aprobación' })
  @ApiOkResponse({ type: CaregiverResponseDto, isArray: true })
  async pending(): Promise<CaregiverResponseDto[]> {
    const list = await this.membership.listPendingCaregivers();
    return list.map(CaregiverResponseDto.from);
  }

  @Post(':id/approve')
  @ApiOperation({ summary: 'UC-19 · Aprobar cuenta (la publica en el marketplace)' })
  @ApiOkResponse({ type: CaregiverResponseDto })
  async approve(
    @Param('id') id: string,
    @CurrentAccount() admin: AuthPrincipal,
  ): Promise<CaregiverResponseDto> {
    return CaregiverResponseDto.from(await this.membership.approveCaregiver(id, admin.accountId));
  }

  @Post(':id/reject')
  @ApiOperation({ summary: 'UC-19 · Rechazar cuenta (con motivo)' })
  @ApiOkResponse({ type: CaregiverResponseDto })
  async reject(
    @Param('id') id: string,
    @Body() dto: RejectCaregiverDto,
    @CurrentAccount() admin: AuthPrincipal,
  ): Promise<CaregiverResponseDto> {
    return CaregiverResponseDto.from(
      await this.membership.rejectCaregiver(id, admin.accountId, dto.reason),
    );
  }

  @Put(':id/badges')
  @ApiOperation({ summary: 'UC-19 · Actualizar insignias de verificación (niveles independientes)' })
  @ApiOkResponse({ type: CaregiverResponseDto })
  async badges(
    @Param('id') id: string,
    @Body() dto: SetBadgesDto,
    @CurrentAccount() admin: AuthPrincipal,
  ): Promise<CaregiverResponseDto> {
    return CaregiverResponseDto.from(
      await this.membership.setCaregiverBadges(id, admin.accountId, dto),
    );
  }
}
