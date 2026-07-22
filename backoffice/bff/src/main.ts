import { NestFactory } from '@nestjs/core';
import { Logger, ValidationPipe } from '@nestjs/common';
import { NestExpressApplication } from '@nestjs/platform-express';
import { ConfigService } from '@nestjs/config';
import type { Request, Response } from 'express';
import cookieParser from 'cookie-parser';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  const cfg = app.get(ConfigService);
  const apiUrl = cfg.get<string>('keruApiUrl')!;
  const cookieName = cfg.get<string>('cookieName')!;
  const webOrigin = cfg.get<string>('webOrigin')!;
  const port = cfg.get<number>('port')!;

  app.use(cookieParser());
  app.enableCors({ origin: webOrigin, credentials: true });
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));

  // Proxy autenticado: /bff/api/* -> Keru API, adjuntando el Bearer guardado en la cookie httpOnly.
  // El browser nunca ve el token; el backend real solo se alcanza a través de esta capa.
  app.use('/bff/api', async (req: Request, res: Response) => {
    const token = req.cookies?.[cookieName];
    if (!token) {
      res.status(401).json({ statusCode: 401, code: 'UNAUTHORIZED', message: 'Sesión requerida' });
      return;
    }
    const target = apiUrl + req.url; // req.url ya viene sin el prefijo /bff/api
    const hasBody = !['GET', 'HEAD', 'DELETE'].includes(req.method);
    try {
      const upstream = await fetch(target, {
        method: req.method,
        headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
        body: hasBody ? JSON.stringify(req.body ?? {}) : undefined,
      });
      const text = await upstream.text();
      res.status(upstream.status);
      res.set('content-type', upstream.headers.get('content-type') ?? 'application/json');
      res.send(text);
    } catch {
      res.status(502).json({ statusCode: 502, code: 'BAD_GATEWAY', message: 'Backend no disponible' });
    }
  });

  await app.listen(port);
  Logger.log(`BFF del back-office en http://localhost:${port} · proxy -> ${apiUrl}`, 'Bootstrap');
}

void bootstrap();
