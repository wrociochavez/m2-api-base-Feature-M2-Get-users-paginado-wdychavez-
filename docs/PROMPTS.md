# Prompts utilizados

Compilación de los prompts del proceso, en orden. Hay dos tipos y se distinguen:

- **Literales:** las peticiones del estudiante a Claude Code durante la sesión, copiadas tal
  cual (con sus erratas).
- **Reconstruidos:** las instrucciones de cada fase del patrón skeleton-first + test-first,
  escritas con el formato de los apuntes de las clases 1 a 3. Describen lo que se le pidió
  a la IA en cada fase; no son una transcripción palabra por palabra.

## A. Prompts literales de la sesión

| # | Prompt (literal) | Qué provocó |
|---|---|---|
| 1 | "Tomar el repositorio base https://github.com/next-gen-coding/m2-api-base implementar algo nuevo en el proyecto … Entregar documento con toda la evidencia y el pull request mandado hacia la Branch del amin del repositorio. Te recomiendo listado de usuarios con paginación, búsqueda y orden (GET /users?q=&page=&size=&sort=) sobre el proyecto base … si gue los formato anexos para elaborar el ejercicio y esta rubrica" (se adjuntaron formato de entrega, rúbrica, plan de reto y `examen.txt`) | Modo plan: lectura del repo y plan de la feature |
| 2 | "usa este folder C:\Users\wchavez\Documents\AI Tec de Monterrey\Evaluaciones\Modulo 2\Examen" | Rechazo del plan; se ajustó la carpeta de trabajo |
| 3 | "mejor usa el folder C:\ClaudePractice\Modulo 2 Maestro Manuel\Examen" | Plan aprobado con esa carpeta |
| 4 | "--Modificar el cloude,md para poner todo lo que pidan de documentacion --actualizar el readme y un codigo de refleccion --poner el claude.md generar una bitacora" | Sección de documentación y bitácora en `CLAUDE.md`; README y reflexión |
| 5 | "continue wsl.exe -l -v 2>&1 \| tr -d '\0' \| head -5" | Comprobar WSL para `mutmut`: sin distribuciones instaladas |
| 6 | "en qu epunto vamos de los archivos anexos de la rubrica, plan y entrega" | Resumen de avance frente a rúbrica, plan y formato |
| 7 | (apuntes de las clases 1 a 4) "nota en los apuntes sobre mutacion que sirva para continuar" | Se usó la mutación manual de la Clase 2 (script propio) |
| 8 | "y ya revisaste lf ormato de entrega, el plan y la rubrica_" | Auditoría punto por punto y lista de pendientes |
| 9 | "1 y 2" | `docs/EVIDENCIA.md` y revisión de redacción |
| 10 | "esto ya esta ? Compila la evidencia: prompts" | Este documento |

## B. Prompts de fase (reconstruidos)

### 1. Contexto (apuntes Clase 1, paso 1)

```
Lee @CLAUDE.md, @users/routes.py, @users/service.py, @users/repository.py,
@users/schemas.py, @core/errors.py y @tests/test_users.py.
Resúmeme las convenciones del proyecto y qué archivos usarías como ejemplo
para extender el recurso users. No cambies nada.
```

Resultado: línea base de 6 tests, 98% de cobertura y `ruff` limpio.

### 2. Esqueleto (Clase 1, paso 2)

```
Quiero extender GET /users con q, page, size y sort, siguiendo el patrón de
@users/routes.py y las convenciones de @CLAUDE.md.
Dame solo el ESQUELETO: el schema UserPage en @users/schemas.py, la ruta con su
firma y response_model, y la función list_users en @users/service.py con docstring.
NO implementes lógica todavía.
```

Revisión: la ruta quedó en `users/routes.py`, con `response_model` y delegando en el servicio.
Cambio respecto al plan: `page` y `size` se validan con `Query(ge, le)` y no con
`invalid_request`.

### 3. Tests en rojo (Clase 2, estructura y edge cases)

```
Escribe tests pytest para GET /users en tests/test_users_list.py. Reglas:
- page >= 1, size entre 1 y 100, sort en {id, name, email, created_at} con '-' = descendente
- q busca sin distinguir mayúsculas en name y email
- respuesta {items, total, page, size, pages}; página fuera de rango -> 200 con items vacío
Un test por caso, nombres en español, arrange/act/assert, aserciones específicas.
Edge cases: page=0, size=0, size=101, sort inválido, q vacío, q sin coincidencias,
idempotencia, empates en el orden. Un test del servicio con el repositorio simulado.
Aún no implementes nada: deben fallar.
```

Resultado: 28 tests fallan y 10 pasan.

### 4. Implementación (Clase 1, incremental)

```
Implementa list_users en @users/service.py con el código mínimo que haga pasar
@tests/test_users_list.py. Reutiliza repository.list_all. Errores con core/errors.
Corre pytest -q y ruff check .
```

Resultado: 38 en verde; `ruff` marcó una línea de más de 100 caracteres y se partió.

### 5. Debugging (Clase 3, hipótesis antes del fix)

Cambio inducido: `start = (page - 1) * size` por `start = page * size`.

```
Este test falla: test_list_users_devuelve_los_seed.
Esperaba: 4 items con total 4.
Obtengo: total 4 pero items == [] (assert 0 == 4).
@users/service.py
NO cambies código todavía. Dame 2-3 hipótesis de la causa, de más a menos probable,
y cómo confirmar cada una.
```

Hipótesis devueltas: H1 offset mal calculado (elegida), H2 `_search` descarta usuarios,
H3 `UserPage` recorta `items`. Después: "Confirmado H1. Aplica el fix mínimo, nada más."

### 6. Refactor (Clase 3, refactor seguro)

```
Revisa @users/service.py y lista los code smells, con la línea y por qué es un problema.
No cambies nada.
```

```
Refactoriza list_users en pasos pequeños: extrae _search, _sort y _paginate, y
SORT_FIELDS como constante. No cambies el comportamiento. Después de cada paso
corre pytest -q.
```

### 7. Integración y mutación (Clase 2, pasos 4 y 5)

```
Corre pytest --cov=users --cov-branch --cov-report=term-missing, lee la columna
Missing y genera tests para lo no cubierto. Añade tests de integración con
TestClient y el repositorio real (crear por POST y luego buscar, ordenar y paginar).
```

```
mutmut no corre en Windows. Escribe scripts/mutation_check.py: aplica una mutación a la
vez sobre @users/service.py (or -> and, off-by-one, quitar el desempate, etc.), corre
la suite, restaura el archivo y reporta mutantes vivos y muertos.
```

```
Sobrevive la mutación "sin desempate por id". Refuerza los tests para matarla:
aserciones específicas, un test por caso, nombre descriptivo en español.
```

Resultado: 14 de 15 mutantes muertos, luego 15 de 15.

### 8. Documentación (Clase 4, documentación que no miente)

```
Genera docstrings estilo Google (Args, Returns, Raises) para @users/service.py.
No cambies la lógica. Revísalos contra lo que la función debería hacer.
Actualiza @README.md (parámetros, ejemplo curl, tests, mutación), crea CHANGELOG.md
y BITACORA.md, y documenta el cambio incompatible de GET /users.
```

## C. Propuestas de la IA rechazadas

| Propuesta | Motivo del rechazo |
|---|---|
| Validar `page` y `size` con `invalid_request` en el servicio | `Query(ge, le)` es más simple y queda en `/docs` |
| Endpoint nuevo en vez de extender `GET /users` | Se pidió extender `GET /users` |
| Usar `mutmut` | No corre en Windows nativo y no hay WSL |
