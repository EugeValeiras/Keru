import { Controller, Get, Param, Post, Query, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOkResponse, ApiOperation, ApiQuery, ApiTags } from '@nestjs/swagger';
import { AuthPrincipal, CurrentAccount, JwtAuthGuard, Roles, RolesGuard } from '@keru/core';
import { ReputationManager } from './manager/reputation.manager';
import { Review } from './resource-access/entities/review.entity';

const toDto = (r: Review) => ({
  id: r.id,
  requestId: r.requestId,
  subjectType: r.subjectType,
  subjectId: r.subjectId,
  rating: r.rating,
  comment: r.comment,
  visibility: r.visibility,
  moderatedBy: r.moderatedBy,
  createdAt: r.createdAt,
});

/** NFR-22 · Moderación de reseñas (back-office). Requiere rol admin. */
@ApiTags('Moderation')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Controller('admin/reviews')
export class AdminReviewController {
  constructor(private readonly reputation: ReputationManager) {}

  @Get()
  @ApiOperation({ summary: 'NFR-22 · Reseñas para moderar (publicadas y retenidas)' })
  @ApiQuery({ name: 'page', required: false, type: Number })
  @ApiQuery({ name: 'pageSize', required: false, type: Number })
  @ApiOkResponse({ description: 'Página de reseñas' })
  async list(@Query('page') page = '1', @Query('pageSize') pageSize = '20') {
    const r = await this.reputation.listReviewsForModeration(Number(page), Number(pageSize));
    return { ...r, items: r.items.map(toDto) };
  }

  @Post(':id/withhold')
  @ApiOperation({ summary: 'NFR-22 · Retener reseña (oculta del público, preserva el original)' })
  async withhold(@Param('id') id: string, @CurrentAccount() admin: AuthPrincipal) {
    return toDto(await this.reputation.moderateReview(id, 'withheld', admin.accountId));
  }

  @Post(':id/publish')
  @ApiOperation({ summary: 'NFR-22 · Republicar reseña retenida' })
  async publish(@Param('id') id: string, @CurrentAccount() admin: AuthPrincipal) {
    return toDto(await this.reputation.moderateReview(id, 'published', admin.accountId));
  }
}
