# API de usuarios — guía del proyecto

API REST de ejemplo (FastAPI + Pydantic v2). Almacén en memoria, sin base de datos:
el proyecto corre sin infraestructura.

## Estructura

- `main.py` — crea la app y monta los routers.
- `users/` — recurso de ejemplo. Cada recurso sigue el mismo patrón:
  - `routes.py` — rutas HTTP. Sin lógica de negocio: delega en `service.py`.
  - `service.py` — lógica de negocio. Única capa que habla con `repository.py`.
  - `schemas.py` — modelos Pydantic de entrada (`*Create`) y salida.
  - `repository.py` — acceso a datos (aquí, un `dict` en memoria).
- `core/errors.py` — catálogo de errores. Toda respuesta de error sale de aquí.
- `tests/` — un archivo por recurso: `test_<recurso>.py`.

## Convenciones

- Las rutas declaran `response_model=` y devuelven modelos Pydantic, nunca `dict` crudos.
- Los errores se levantan con las funciones de `core/errors.py`
  (`not_found`, `invalid_request`, `already_exists`), no con `HTTPException` a mano.
- La ruta delega en `service.py`; la lógica y las decisiones de error viven ahí.
- Identificadores en inglés y `snake_case`, sin abreviaturas. Mensajes de error en español.
- Cada endpoint nuevo lleva su test en el archivo del recurso, con al menos un caso
  feliz y un caso de error.
- Rutas específicas antes que rutas con parámetro: `/users/search` debe declararse
  **antes** de `/users/{user_id}`.

## Listados (paginación, búsqueda y orden)

- Los listados aceptan `q`, `page` (≥1), `size` (1–100) y `sort` (`campo` o `-campo`).
- Devuelven una página `{items, total, page, size, pages}` (`UserPage`), nunca una lista cruda.
- `page`/`size` se validan en la ruta con `Query(...)` (422 automático); un `sort` con
  campo no permitido lo rechaza `service.py` con `errors.invalid_request`.
- El orden siempre desempata por `id` para que la paginación sea estable.

## Documentación y bitácora (obligatorio en cada feature)

Toda feature debe dejar, además del código y los tests:

1. **Docstrings** (en español, estilo Args/Returns/Raises) en funciones públicas de
   `service.py` y en los helpers no triviales.
2. **README.md** actualizado: endpoints nuevos con ejemplos `curl`, parámetros,
   cómo correr tests/cobertura/mutation testing y enlaces a la bitácora y al changelog.
3. **CHANGELOG.md** (formato Keep a Changelog): fecha, versión y resumen de cambios,
   marcando los cambios incompatibles (*breaking*).
4. **BITACORA.md**: el agente debe **generar y mantener una bitácora** del proceso —
   una fila por iteración con fase, prompt resumido, resultado y decisión
   (aceptado/rechazado y por qué). Incluye los bugs: stack trace, hipótesis propuestas
   (se pide hipótesis *antes* del fix), hipótesis elegida, fix y validación.
5. **docs/REFLEXION.md**: reflexión final (qué funcionó, qué no, qué mejorar, límites
   de la IA) con evidencia: logs de `pytest`, cobertura y mutation testing.

Flujo de trabajo: skeleton-first (firmas sin implementación) → tests en rojo →
implementación incremental → refactor con tests en verde. Commits pequeños por fase.

## Cómo ejecutar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload          # API en http://127.0.0.1:8000  ·  /docs para el Swagger
pytest                             # tests
pytest --cov=. --cov-branch --cov-report=term-missing   # cobertura (líneas + ramas)
ruff check .                       # linter
mutmut run                         # mutation testing (ver README)
```

## Fuera de límites

- `migrations/` y `legacy/` — no modificar.
