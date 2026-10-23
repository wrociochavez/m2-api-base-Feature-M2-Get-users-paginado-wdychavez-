# Bitácora del proceso (IA)

Feature: `GET /users?q=&page=&size=&sort=` — patrón **skeleton-first + test-first incremental**.

| # | Fase | Prompt resumido | Resultado / decisión |
|---|------|-----------------|----------------------|
| 1 | Contexto | Leer CLAUDE.md, users/*, core/errors.py, tests/ | Baseline: 6 tests, 98% cobertura, ruff limpio |
| 2 | Skeleton | Generar firmas (`UserPage`, `service.list_users`, ruta con `Query`) sin implementación | Aceptado; service lanza `NotImplementedError` |
