# Keru — Repo paraguas

Este repositorio **no contiene código de aplicación**. Es el paraguas del proyecto Keru:
agrupa los sub-repos, la documentación de producto/arquitectura y la configuración de
agentes (`.claude`, `addl`) que permiten entender el **scope general** del proyecto.

Keru es un **marketplace de cuidadores** ("el Uber de los cuidadores"): conecta pacientes
y sus familias con cuidadores profesionales, permite contratarlos en línea, registrar las
métricas de salud del paciente y que la familia consulte la evolución y reciba alertas.

## Sub-repositorios

Cada uno vive en su propio repo Git (están **ignorados** por este paraguas — ver `.gitignore`)
y se clona dentro de esta carpeta:

| Carpeta | Repo | Rol |
|---|---|---|
| `Keru-API/` | [EugeValeiras/Keru-API](https://github.com/EugeValeiras/Keru-API) | Backend NestJS (monolito modular, 5 dominios) — API REST |
| `Keru-App/` | [EugeValeiras/Keru-App](https://github.com/EugeValeiras/Keru-App) | App móvil (cliente) |
| `Keru-Webapp/` | [EugeValeiras/Keru-Webapp](https://github.com/EugeValeiras/Keru-Webapp) | Web cliente (Angular) |

Para trabajar en el proyecto completo, clonalos dentro de esta carpeta:

```bash
git clone https://github.com/EugeValeiras/Keru-API.git
git clone https://github.com/EugeValeiras/Keru-App.git
git clone https://github.com/EugeValeiras/Keru-Webapp.git
```

## Documentación de scope (fuente de verdad)

- `Keru-Casos-de-Uso-MVP.md` — casos de uso del MVP (fuente de verdad de producto).
- `Keru-Scope-MVP.docx.pdf` — alcance / scope de salida original.
- `constitution.md` — reglas no-negociables (arquitectura, NFRs, alcance).
- `addl/docs/architect/residual-design.md` — diseño arquitectónico completo (IDesign residual).
- `.claude/` · `addl/.claude/` — skills y agentes del proyecto (incluido el skill `keru-feature`, flujo docs-first).
