# Bitácora del proceso (IA)

Feature: `GET /users?q=&page=&size=&sort=` sobre `m2-api-base`.
Patrón: **skeleton-first + test-first, en cadencia incremental** (un commit por fase).
Herramienta: Claude Code (modelo Sonnet 5.5) en modo plan y luego ejecución.

## 1. Especificación y contexto

- Criterios de aceptación en el plan: `q` insensible a mayúsculas en nombre/email;
  `page` ≥ 1; `size` 1–100; `sort` ∈ {id, name, email, created_at} con `-` = descendente;
  respuesta `{items, total, page, size, pages}`; página fuera de rango → 200 con `items: []`;
  `sort` inválido → 422.
- Contexto entregado a la IA: `CLAUDE.md`, `users/routes.py`, `service.py`, `repository.py`,
  `schemas.py`, `core/errors.py`, `tests/conftest.py`, `tests/test_users.py` y los apuntes
  de las clases 1–4.
- Línea base: 6 tests, 98% de cobertura, `ruff` limpio.

## 2. Iteraciones

| # | Fase | Prompt / petición (resumida) | Resultado | Decisión |
|---|------|------------------------------|-----------|----------|
| 1 | Contexto | Leer el repo y resumir convenciones; no cambiar nada | Baseline 6 tests, 98% | — |
| 2 | Skeleton | Firmas de `UserPage`, `service.list_users` (docstring, sin lógica) y ruta con `Query` | Commit `e05dae7`; service lanza `NotImplementedError` | Aceptado. Validar `page`/`size` con `Query(ge, le)` en vez de `invalid_request`: es lo idiomático en FastAPI |
| 3 | Test-first | Escribir tests en rojo: paginación, búsqueda, orden, 422, idempotencia, mock del repo | 28 fallan, 10 pasan (commit `0c55c64`) | Se actualizó `test_list_users_devuelve_los_seed` por el cambio de forma de respuesta |
| 4 | Implementación | Código mínimo que pone la suite en verde | 38 verdes (commit `f868736`); ruff marcó una línea > 100 y se partió | Aceptado |
| 5 | Bug inducido | Cambiar `(page - 1) * size` por `page * size` | Ver §3 | Hipótesis H1 elegida |
| 6 | Refactor | Extraer `_search`, `_sort`, `_paginate` (commit `5617fc5`) | 38 verdes antes y después; 100% de cobertura | Aceptado |
| 7 | Integración | Tests con `TestClient` y repositorio real; test de `/health` (commit `c91a8fd`) | 42 verdes, 100% líneas y ramas | Aceptado |
| 8 | Mutación | `mutmut` no corre en Windows (error: "please use the WSL"); WSL sin distribución | Script propio `scripts/mutation_check.py` con 15 mutantes | Rechazado mutmut; ver §4 |
| 9 | Docs | README, CHANGELOG, CLAUDE.md, esta bitácora y reflexión | Versión 0.2.0 | — |

## 3. Debugging asistido (bug inducido)

- **Reproducción:** con el offset roto (`start = page * size`), la suite falla en el primer test.
  Log completo en [docs/evidencia/bug1_offbyone_log.txt](docs/evidencia/bug1_offbyone_log.txt):

  ```
  FAILED tests/test_users.py::test_list_users_devuelve_los_seed - assert 0 == 4
  E       assert 0 == 4
  E        +  where 0 = len([])
  ```
- **Hipótesis (pedidas antes del fix, de más a menos probable):**
  - **H1 — offset de la página mal calculado:** `total` es correcto (4) pero `items` está
    vacío en la página 1; el slice empieza más allá del final. Se confirma leyendo la
    línea `start = ...` y comparando con `page=1`.
  - H2 — el filtro `_search` descarta usuarios: improbable, `q` no se envía en ese test.
  - H3 — `UserPage` recorta `items`: improbable, es un modelo sin validadores de longitud.
- **Hipótesis elegida:** H1, porque `total == 4` y `items == []` descarta H2 y H3.
- **Fix mínimo:** restaurar `start = (page - 1) * size`. Validación: 38 tests en verde
  (ya existían tests de la página 1 y 2 que habrían fallado; no hizo falta test nuevo).
- **Limitación honesta:** el bug lo introduje yo a propósito, así que la "confirmación" fue
  fácil. Las pruebas de paginación existentes son las que lo detectaron.
- **No realizado:** el "caso de prueba erróneo" que menciona el guion del examen
  (`examen.txt`). Queda como mejora.

## 4. Decisiones sobre propuestas de la IA

| Propuesta | Decisión | Motivo |
|-----------|----------|--------|
| Validar `page`/`size` en `service.py` con `errors.invalid_request` (plan inicial) | Rechazada | `Query(ge=1, le=100)` da 422 sin código extra y queda documentado en `/docs` |
| `mutmut` para mutation testing | Rechazada | No corre en Windows nativo ni hay WSL; los apuntes de la clase 2 validan la mutación manual |
| Crear `GET /users/search` como endpoint nuevo (alternativa) | Rechazada | Se pidió extender `GET /users` |
| Primera corrida de mutación: 14/15, sobrevive "sin desempate por id" | Aceptada y corregida | Test `test_service_orden_desempata_por_id_cuando_el_campo_es_igual`; segunda corrida 15/15 |

## 5. Resultados

- 43 tests en verde, 100% de cobertura de líneas y ramas
  ([cobertura_final.txt](docs/evidencia/cobertura_final.txt)).
- Mutation score: 14/15 (93%) → 15/15 (100%) tras el test de desempate
  ([corrida 1](docs/evidencia/mutacion_corrida1.txt), [corrida 2](docs/evidencia/mutacion_corrida2.txt)).
- `ruff check .` limpio.
