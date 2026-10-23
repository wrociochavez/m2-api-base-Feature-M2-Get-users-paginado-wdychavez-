# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [0.2.0] - 2026-10-23

### Añadido
- `GET /users` acepta `q` (búsqueda en nombre/email), `page`, `size` (1–100) y `sort`
  (`id`, `name`, `email`, `created_at`; `-campo` = descendente).
- Schema `UserPage` (`items`, `total`, `page`, `size`, `pages`).
- Helpers `_search`, `_sort` y `_paginate` en `users/service.py` con docstrings.
- `tests/test_users_list.py` (unitarios y edge cases) y
  `tests/test_users_list_integration.py` (flujo crear → buscar → ordenar → paginar).
- `scripts/mutation_check.py`: mutation testing manual (15 mutantes, 100% muertos).
- `BITACORA.md`, `docs/REFLEXION.md` y `docs/evidencia/`.

### Cambiado
- **Incompatible:** `GET /users` devuelve `UserPage` en lugar de `list[User]`.
- `CLAUDE.md`: convenciones de listados y requisitos de documentación y bitácora.
- Versión de la API y del proyecto: 0.2.0.

### Corregido
- Off-by-one en el cálculo del offset de paginación detectado durante el desarrollo
  (bug inducido para la práctica de debugging; nunca llegó a una versión publicada).

## [0.1.0]
- Versión base: `GET /health`, `GET /users`, `GET /users/{id}`, `POST /users`.
