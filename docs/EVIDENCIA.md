# Evidencia del reto — Módulo 2: Desarrollo y testing con IA

**Feature:** listado de usuarios con paginación, búsqueda y orden — `GET /users?q=&page=&size=&sort=`
**Proyecto base:** [next-gen-coding/m2-api-base](https://github.com/next-gen-coding/m2-api-base) (FastAPI + Pydantic v2)
**Rama:** `feature/users-list-pagination` · **Versión:** 0.2.0 · **Fecha:** 23 de octubre de 2026
**Herramienta de IA:** Claude Code (Sonnet 5.5)

> Nota sobre el plan de reto: sobre los edge cases de una API de *tareas* (título
> inválido, fecha pasada, prioridad fuera de rango, idempotencia). El proyecto base es una API
> de *usuarios*, así que se adaptaron esos casos a esta feature: `page` o `size` fuera de rango,
> `sort` inválido, `q` vacío o sin coincidencias, página fuera de rango e idempotencia del GET.

---

## 1. Especificación de la funcionalidad y preparación de contexto

### a) Descripción

- **Objetivo:** permitir consultar usuarios sin traer toda la lista, buscando por texto,
  ordenando y paginando.
- **Alcance:** solo `GET /users`. No se modifican `POST /users`, `GET /users/{id}` ni los
  directorios `migrations/` y `legacy/`.
- **Criterios de aceptación:**

| Aspecto | Criterio |
|---|---|
| `q` | Texto opcional; busca sin distinguir mayúsculas en `name` o `email`. Vacío o solo espacios: no filtra. |
| `page` | Entero ≥ 1, por defecto 1. Fuera de rango: **422**. |
| `size` | Entero de 1 a 100, por defecto 10. Fuera de rango: **422**. |
| `sort` | `id`, `name`, `email` o `created_at`; prefijo `-` para descendente; por defecto `id`. Campo no permitido: **422**. Desempata por `id`. |
| Respuesta **200** | `{items: [User], total, page, size, pages}` |
| Página más allá del final | **200** con `items: []` y `total` correcto. |
| Idempotencia | El GET no modifica el almacén; la misma consulta devuelve lo mismo. |

### b) Contexto entregado a la IA

- Archivos (`@file`): `CLAUDE.md`, `users/routes.py`, `users/service.py`, `users/repository.py`,
  `users/schemas.py`, `core/errors.py`, `tests/conftest.py`, `tests/test_users.py`.
- Tipos existentes: `User`, `UserCreate` (Pydantic). Interfaz reutilizada: `repository.list_all()`.
- Convenciones del proyecto (de `CLAUDE.md`): rutas sin lógica, errores vía `core/errors.py`,
  identificadores en inglés, mensajes en español, tests con arrange/act/assert.
- Actualicé `CLAUDE.md` con las convenciones de listados y los requisitos de documentación
  y bitácora.
- Línea base antes de empezar: 6 tests, 98% de cobertura, `ruff` limpio.

### c) Patrón elegido y justificación

**Skeleton-first + test-first, en cadencia incremental.**

- *Skeleton-first:* la feature toca cuatro piezas (schema, ruta, servicio, validación). Revisar
  las firmas antes de escribir lógica detecta errores de diseño cuando cuestan pocas líneas.
- *Test-first:* los criterios son claros y verificables (códigos HTTP, forma de la respuesta),
  así que los tests sirven como especificación y como red de seguridad para el refactor.
- *Incremental:* un commit por fase (esqueleto → tests en rojo → implementación → refactor →
  integración → mutación → documentación).

---

## 2. Generación de código asistida por IA

### a) Iteraciones (solicitud → revisión → refinamiento)

| # | Solicitud | Revisión | Refinamiento / commit |
|---|---|---|---|
| 1 | Leer el repo y resumir convenciones | Baseline correcto | — |
| 2 | Esqueleto sin lógica | Verifiqué que la ruta está en `users/routes.py`, tiene `response_model` y delega en el servicio | `e05dae7` |
| 3 | Tests en rojo | 28 fallan y 10 pasan, como se esperaba | `0c55c64` |
| 4 | Implementación mínima | 38 en verde; `ruff` marcó una línea de más de 100 caracteres | Se partió la línea; `f868736` |
| 5 | Refactor | 38 en verde antes y después | `5617fc5` |

Fragmento del esqueleto (paso 2):

```python
def list_users(q: str | None = None, page: int = 1, size: int = 10, sort: str = "id") -> UserPage:
    """Lista usuarios con búsqueda, orden y paginación. ..."""
    raise NotImplementedError
```

Fragmento de la ruta final (sin lógica de negocio, validación declarativa):

```python
@router.get("", response_model=UserPage)
def list_users(
    q: str | None = Query(None, description="Busca en nombre o email"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Usuarios por página"),
    sort: str = Query("id", description="Campo de orden; `-` al inicio para descendente"),
) -> UserPage:
    return service.list_users(q=q, page=page, size=size, sort=sort)
```

### b) Integración con el codebase y estilo

- Misma estructura de capas: ruta → servicio → repositorio. La ruta no contiene lógica.
- El error de `sort` sale del catálogo: `errors.invalid_request(...)`, no de un `HTTPException`.
- Se reutiliza `repository.list_all()`; no se tocó el repositorio.
- Se añadió el schema `UserPage` junto a `User` en `users/schemas.py`.
- `ruff check .` limpio (reglas E, F, I, UP, B del proyecto).

### c) Decisiones clave

| Propuesta | Decisión | Motivo |
|---|---|---|
| Validar `page` y `size` en el servicio con `invalid_request` | Rechazada | `Query(ge=1, le=100)` da 422 sin código extra y queda en `/docs` |
| Endpoint nuevo en lugar de extender `GET /users` | Rechazada | Se pidió extender `GET /users`. Consecuencia: cambio incompatible, registrado en el CHANGELOG |
| `mutmut` para mutation testing | Rechazada | No corre en Windows nativo y no hay WSL; se usó un script propio |
| Orden con desempate por `id` | Aceptada | Hace estable la paginación. Un mutante la puso a prueba (ver sección 3) |

---

## 3. Suite de tests y cobertura

### a) Unitarios

Archivo `tests/test_users_list.py`. Estructura arrange / act / assert con nombres descriptivos
en español y aserciones específicas. Ejemplo:

```python
def test_list_users_pagina_2_con_size_2(client: TestClient) -> None:
    response = client.get("/users", params={"page": 2, "size": 2})

    assert _ids(response) == [3, 4]
```

Mock de dependencias: el servicio se prueba con el repositorio simulado (`monkeypatch`),
sin tocar el almacén real:

```python
monkeypatch.setattr(repository, "list_all", lambda: usuarios)
page = service.list_users(size=3, page=3)
assert (page.total, page.pages) == (7, 3)
```

Edge cases cubiertos: `page=0`, `page=-1`, `page="abc"`, `size=0`, `size=101`, `size=100`
(límite válido), página fuera de rango, `q` sin coincidencias, `q` vacío o solo espacios,
`q` con espacios alrededor, mayúsculas en `q` y en el orden, `sort` inválido (`password`, `-`,
vacío, `name,id`, `-ID`), empates en el campo de orden, idempotencia y no modificación del
almacén.

### b) Integración

Archivo `tests/test_users_list_integration.py`. Usa el `TestClient` y el repositorio real.
Las fixtures vienen de `tests/conftest.py`: `_reset_data` (autouse) restablece el almacén
antes y después de cada prueba (setup/teardown), y `client` crea el cliente.

- `test_flujo_crear_buscar_ordenar_y_paginar`: crea tres usuarios por la API y luego los busca,
  ordena y pagina.
- `test_usuario_creado_aparece_en_el_total_del_listado`.
- `test_listado_y_detalle_son_consistentes`.
- `test_health_responde_ok` (cubre `main.py`).

### c) Resultados

```
Name                  Stmts   Miss Branch BrPart  Cover
users\repository.py      23      0      2      0   100%
users\routes.py          13      0      0      0   100%
users\schemas.py         15      0      0      0   100%
users\service.py         34      0      8      0   100%
core\errors.py            7      0      0      0   100%
main.py                   7      0      0      0   100%
TOTAL                    99      0     10      0   100%
43 passed
```

| Medida | Antes | Después |
|---|---|---|
| Tests | 6 | 43 |
| Cobertura (líneas y ramas) | 98% | 100% |
| Mutantes muertos | — | 15 de 15 |

**Mutation testing** (`python scripts/mutation_check.py`): el script aplica 15 mutaciones, una
por vez (por ejemplo `or` → `and`, `(page - 1) * size` → `page * size`, quitar el desempate
por `id`), corre la suite y restaura el archivo. En la primera corrida sobrevivió 1 mutante
(*sin desempate por id*). Aunque la cobertura ya era del 100%, ningún test comprobaba el
desempate. Se Añade `test_service_orden_desempata_por_id_cuando_el_campo_es_igual` y la segunda
corrida terminó en 15/15. Logs en `docs/evidencia/`.

---

## 4. Debugging y refactorización asistidos

### a) Bug y debugging

El bug se introdujo a propósito: `start = (page - 1) * size` → `start = page * size`.

- **Fallo observado** (`docs/evidencia/bug1_offbyone_log.txt`):

  ```
  FAILED tests/test_users.py::test_list_users_devuelve_los_seed - assert 0 == 4
  E       +  where 0 = len([])
  ```
- **Hipótesis pedidas antes del fix:**
  - **H1:** offset de página mal calculado (`total` correcto, `items` vacío en la página 1).
  - H2: el filtro `_search` descarta usuarios (poco probable: ese test no envía `q`).
  - H3: `UserPage` recorta `items` (poco probable: el modelo no tiene validadores de longitud).
- **Elegida:** H1, porque `total == 4` e `items == []` descartan H2 y H3.
- **Fix mínimo:** restaurar `(page - 1) * size`. **Validación:** la suite completa volvió a verde.
- **Limitaciones:** el bug es introducido, por lo que confirmar la causa fue sencillo.

### b) Refactorización

Con 38 tests en verde se extrajo la lógica de `list_users` a tres funciones pequeñas, un
refactor por commit:

```python
def list_users(q=None, page=1, size=10, sort="id") -> UserPage:
    users = _sort(_search(repository.list_all(), q), sort)
    return _paginate(users, page, size)
```

Los tests actuaron como red de seguridad: se corrieron antes y después y no hubo que cambiar
ninguno. Smells atendidos: función larga con tres responsabilidades y valores mágicos
(`SORT_FIELDS` ahora es una constante).

### c) Resultados

Mayor claridad (cada helper tiene una responsabilidad y su docstring), mejor mantenibilidad
(agregar un campo de orden es editar una tupla) y estabilidad (43 tests en verde, 15 de 15
mutantes muertos).

---

## 5. Documentación y evidencia del proceso

### a) Docstrings y README

- Docstrings en español, estilo Args/Returns/Raises, en `service.list_users` y en los helpers
  `_search`, `_sort` y `_paginate`.
- `README.md`: tabla de parámetros, ejemplo `curl` con respuesta, comandos de tests,
  cobertura y mutación, y enlaces a la bitácora y al changelog.

### b) Changelog

[`CHANGELOG.md`](../CHANGELOG.md): versión 0.2.0 (2026-10-23) con lo añadido, lo cambiado
(**incompatible:** `GET /users` ahora devuelve `UserPage`) y lo corregido.

### c) Evidencia del proceso

| Archivo | Contenido |
|---|---|
| [`BITACORA.md`](../BITACORA.md) | Iteraciones, prompts resumidos, bug con hipótesis y decisiones |
| [`docs/PROMPTS.md`](PROMPTS.md) | Prompts utilizados: literales de la sesión y reconstruidos por fase |
| [`docs/evidencia/`](evidencia/) | Logs de cobertura, del bug y de las dos corridas de mutación |
| [`docs/REFLEXION.md`](REFLEXION.md) | Qué funcionó, qué no y qué mejoraría |
| `git log` | Un commit por fase del proceso |

### Reflexión breve

Lo que más ayudó fue definir el contexto y criterios de aceptacion  antes de implementar: el uso de Skeleton First e Incremental permitio cada cambio de forma segua  y los tests en rojo
hicieron que la implementación y el refactor fueran casi mecánicos.La cobertura y las pruebas de mutación ayudaron a detectar casos que inicialmente no estaban contemplados. Como mejora, incluiría más evidencia de las iteraciones realizadas con la IA y documentaría explícitamente las alternativas descartadas durante el proceso. La mutación mostró algo
que el 100% de cobertura no mostraba (el desempate por `id` no estaba verificado). Para
mejorar: registrar los prompts de forma literal desde el
inicio y versionar la ruta o avisar a los consumidores por el cambio incompatible de
`GET /users`. La reflexión completa está en `docs/REFLEXION.md`.
