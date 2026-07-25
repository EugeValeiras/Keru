import {
  Body,
  Controller,
  ForbiddenException,
  Get,
  HttpCode,
  Post,
  Req,
  Res,
  UnauthorizedException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Request, Response } from 'express';
import { LoginDto, StepUpDto } from './dto';
import { sessionCookieOptions, stepUpCookieOptions } from '../config';

interface KeruAuthResponse {
  accessToken: string;
  accountId: string;
  email: string;
  role: string;
  displayName: string;
}

/**
 * Auth del back-office (patrón BFF). El BFF intercambia credenciales con el backend real, guarda el
 * JWT en una cookie httpOnly (el browser nunca lo ve en JS) y solo devuelve datos no sensibles.
 * El back-office es exclusivo de administradores: un login con otro rol se rechaza.
 */
@Controller('bff/auth')
export class AuthController {
  private readonly cookieName: string;
  private readonly stepUpCookieName: string;
  private readonly apiUrl: string;
  private readonly secure: boolean;

  constructor(cfg: ConfigService) {
    this.cookieName = cfg.get<string>('cookieName')!;
    this.stepUpCookieName = cfg.get<string>('stepUpCookieName')!;
    this.apiUrl = cfg.get<string>('keruApiUrl')!;
    this.secure = cfg.get<boolean>('cookieSecure')!;
  }

  @Post('login')
  @HttpCode(200)
  async login(@Body() dto: LoginDto, @Res({ passthrough: true }) res: Response) {
    const r = await fetch(`${this.apiUrl}/auth/login`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(dto),
    });
    if (!r.ok) throw new UnauthorizedException('Credenciales inválidas');

    const auth = (await r.json()) as KeruAuthResponse;
    if (auth.role !== 'admin') {
      throw new ForbiddenException('El back-office es solo para administradores');
    }

    res.cookie(this.cookieName, auth.accessToken, sessionCookieOptions(this.secure));
    return { accountId: auth.accountId, email: auth.email, role: auth.role, displayName: auth.displayName };
  }

  @Post('logout')
  @HttpCode(200)
  logout(@Res({ passthrough: true }) res: Response) {
    res.clearCookie(this.cookieName, sessionCookieOptions(this.secure));
    res.clearCookie(this.stepUpCookieName, stepUpCookieOptions(this.secure));
    return { ok: true };
  }

  /** NFR-33 · Step-up: reingresar la contraseña emite un token de vida corta (cookie httpOnly). */
  @Post('step-up')
  @HttpCode(200)
  async stepUp(@Body() dto: StepUpDto, @Req() req: Request, @Res({ passthrough: true }) res: Response) {
    const session = req.cookies?.[this.cookieName];
    if (!session) throw new UnauthorizedException('Sin sesión');
    const r = await fetch(`${this.apiUrl}/auth/step-up`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', authorization: `Bearer ${session}` },
      body: JSON.stringify(dto),
    });
    if (!r.ok) throw new UnauthorizedException('Contraseña incorrecta');
    const { stepUpToken } = (await r.json()) as { stepUpToken: string };
    res.cookie(this.stepUpCookieName, stepUpToken, stepUpCookieOptions(this.secure));
    return { ok: true };
  }

  @Get('me')
  me(@Req() req: Request) {
    const token = req.cookies?.[this.cookieName];
    if (!token) throw new UnauthorizedException('Sin sesión');
    try {
      const payload = JSON.parse(
        Buffer.from(String(token).split('.')[1], 'base64url').toString(),
      );
      return { accountId: payload.sub, email: payload.email, role: payload.role };
    } catch {
      throw new UnauthorizedException('Sesión inválida');
    }
  }
}
