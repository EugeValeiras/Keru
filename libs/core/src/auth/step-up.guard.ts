import { CanActivate, ExecutionContext, ForbiddenException, Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';
import { AuthPrincipal } from './auth-principal';

/**
 * StepUpGuard (NFR-33). Exige una re-confirmación de identidad reciente para operaciones sensibles:
 * además del JWT de sesión, la request debe traer un "step-up token" válido (header `x-step-up`),
 * emitido tras reingresar la contraseña y con vida corta. Corre DESPUÉS de JwtAuthGuard.
 */
@Injectable()
export class StepUpGuard implements CanActivate {
  constructor(private readonly jwt: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request & { account?: AuthPrincipal }>();
    const token = request.headers['x-step-up'];
    if (!token || typeof token !== 'string') {
      throw new ForbiddenException('Esta acción requiere confirmar tu identidad (step-up)');
    }
    try {
      const payload = await this.jwt.verifyAsync<{ sub: string; stepUp?: boolean }>(token);
      if (!payload.stepUp || payload.sub !== request.account?.accountId) throw new Error('invalid');
      return true;
    } catch {
      throw new ForbiddenException('Confirmación de identidad inválida o expirada');
    }
  }
}
