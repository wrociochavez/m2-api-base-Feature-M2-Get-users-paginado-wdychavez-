# m2-api-base

API REST de usuarios usada como base en el **Módulo 2 · Clase 1 — Generación de código con IA**.

Es un proyecto pequeño pero completo: tiene convenciones, capas separadas, catálogo
de errores y una suite de tests que pasa. Le falta **una** feature — la que vas a
construir en el laboratorio.

## Requisitos

- Python 3.10 o superior
- (Recomendado) Claude Code instalado

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
uvicorn main:app --reload          # http://127.0.0.1:8000  ·  Swagger en /docs
```

Endpoints actuales:

| Método | Ruta              | Descripción                     |
|--------|-------------------|---------------------------------|
| GET    | `/health`         | Estado del servicio             |
| GET    | `/users`          | Lista paginada con búsqueda y orden (ver abajo) |
| GET    | `/users/{id}`     | Un usuario por id (404 si no existe) |
| POST   | `/users`          | Crea un usuario (409 si el email ya existe) |

### Listado de usuarios: `GET /users?q=&page=&size=&sort=`

| Parámetro | Default | Regla |
|-----------|---------|-------|
| `q`       | —       | Texto a buscar (sin distinguir mayúsculas) en `name` o `email`. Vacío = sin filtro. |
| `page`    | `1`     | Entero ≥ 1. |
| `size`    | `10`    | Entero entre 1 y 100. |
| `sort`    | `id`    | `id`, `name`, `email` o `created_at`; prefijo `-` para descendente. Desempata por `id`. |

Errores: **422** si `page`/`size` están fuera de rango o `sort` tiene un campo no permitido.
Una página más allá del final responde **200** con `items: []`.

```bash
curl "http://127.0.0.1:8000/users?q=example.com&sort=-name&page=1&size=2"
```

```json
{
  "items": [
    {"id": 4, "name": "Katherine Johnson", "email": "katherine@example.com", "created_at": "..."},
    {"id": 3, "name": "Grace Hopper", "email": "grace@example.com", "created_at": "..."}
  ],
  "total": 4, "page": 1, "size": 2, "pages": 2
}
```

> **Cambio incompatible (v0.2.0):** `GET /users` ya no devuelve una lista cruda sino la
> página `{items, total, page, size, pages}`. Ver [CHANGELOG.md](CHANGELOG.md).

## Tests y calidad

```bash
pytest                                                  # correr la suite (43 tests)
pytest --cov=. --cov-branch --cov-report=term-missing   # cobertura de líneas y ramas
ruff check .                                            # linter
python scripts/mutation_check.py                        # mutation testing manual sobre users/service.py
```

Resultados actuales: **43 tests en verde, 100% de cobertura (líneas y ramas) y 15/15
mutantes muertos**. `mutmut` no corre en Windows nativo, por eso el script aplica
mutaciones a mano (una por vez), corre la suite y restaura el archivo.

## Proceso y documentación

- [BITACORA.md](BITACORA.md) — prompts, decisiones, bug inducido con hipótesis y refactor.
- [CHANGELOG.md](CHANGELOG.md) — cambios por versión.
- [docs/EVIDENCIA.md](docs/EVIDENCIA.md) — documento de evidencia (secciones 1 a 5 del formato de entrega).
- [docs/PROMPTS.md](docs/PROMPTS.md) — prompts utilizados (literales y reconstruidos).
- [docs/REFLEXION.md](docs/REFLEXION.md) — reflexión final.
- [docs/evidencia/](docs/evidencia/) — logs de cobertura, bug y mutación.

## Ramas del módulo

`main` es la base de la **Clase 1**. Cada clase tiene su rama de trabajo y su
rama de solución:

| Clase | Rama de trabajo | Solución | Qué añade |
|-------|-----------------|----------|-----------|
| 1 · Generación | `main` | `solucion-clase1` | La base. Falta `GET /users/search`. |
| 2 · Testing | `clase2-testing` | `solucion-clase2` | `users/validation.py` sin tests → llévalo a >80%. |
| 3 · Debugging | `clase3-debugging` | `solucion-clase3` | Recurso `reports/` con 3 bugs plantados. |
| 4 · Review | `clase4-review` | `solucion-clase4` | PR de `GET /reports/export` con issues (verde). |

```bash
git switch clase2-testing     # o la que toque
```

## Tarea del laboratorio (Clase 1)

Añadir `GET /users/search?email=<email>`:

- **200** con el usuario si existe
- **422** si el formato del email es inválido
- **404** si no hay ningún usuario con ese email
- con su test en `tests/test_users.py`, siguiendo el estilo del archivo

Lee `CLAUDE.md` antes de empezar: ahí están las convenciones que tu código debe respetar.
