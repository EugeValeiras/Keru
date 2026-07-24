# Atribuciones de assets de terceros

## Íconos — Lucide (KER-77)

Las insignias por-certificación del cuidador (UC-02/UC-19) usan íconos SVG del set
[**Lucide**](https://lucide.dev) — el set de referencia del brand book §5. Se eligieron desde
[icons0.dev](https://icons0.dev) (agregador) y se **bundlean localmente** como SVG inline en el
componente `kr-cert-icon` de la webapp (`src/app/shared/ui/kr-cert-icon.ts`); **no** se hotlinkea
ningún host externo en runtime.

- **Versión**: `lucide-static` v1.26.0
- **Licencia**: ISC (permisiva; solo exige conservar el aviso de copyright, incluido abajo)
- Ninguno de los íconos usados deriva del proyecto Feather (esos van bajo MIT); todos son Lucide puro.

### Íconos usados (iconKey → certificación)

| iconKey | Certificación |
|---|---|
| `stethoscope` | Título de Enfermería |
| `syringe` | Auxiliar de Enfermería |
| `heart-pulse` | RCP |
| `ambulance` | Primeros Auxilios |
| `accessibility` | Cuidado Geriátrico |
| `bird` | Cuidados Paliativos |
| `brain` | Cuidado de Demencia / Alzheimer |
| `bone` | Kinesiología |
| `heart-handshake` | Acompañante Terapéutico |
| `baby` | Enfermería Pediátrica |
| `apple` | Diabetes y Nutrición |
| `award` | Genérico (fallback de un tipo sin ícono propio) |

### Licencia ISC (Lucide)

```
ISC License

Copyright (c) 2026 Lucide Icons and Contributors

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```
