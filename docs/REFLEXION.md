# Reflexión final

## Qué funcionó

- **Skeleton-first + test-first:** fijar el contrato (firmas y tests en rojo) antes de
  implementar hizo que la implementación fuera casi mecánica y que el refactor posterior
  (extraer `_search`, `_sort`, `_paginate`) no tuviera riesgo: 38 tests verdes antes y después.
- **Contexto concreto:** darle a la IA `CLAUDE.md`, el patrón de `routes.py` y el estilo de
  `test_users.py` produjo código que encajó con el repo (capas, errores en español, `response_model`).
- **La mutación como termómetro:** con 100% de cobertura, un mutante sobrevivió (el desempate
  por `id`). La cobertura no lo detectaba; la mutación sí. Es la lección de la Clase 2.
- **Hipótesis antes del fix:** con `total == 4` e `items == []` se descartaron dos hipótesis
  sin tocar código.

## Qué no funcionó o fue limitado

- `mutmut` no soporta Windows nativo: hubo que escribir un script propio con solo 15 mutantes,
  menos exhaustivo que una herramienta real.
- El bug de debugging fue **inducido por mí**, no un fallo real, así que la parte de "confirmar
  la causa" es menos exigente que en un caso real. Tampoco se hizo el caso de prueba erróneo.
- La "evidencia de prompts" es un resumen de las peticiones, no una transcripción literal.
- Algunos supuestos del diseño los tomé yo (por ejemplo, orden descendente con desempate por
  `id` descendente); están documentados pero no los validó un usuario final.

## Qué mejoraría

1. Ejecutar `mutmut` en WSL o CI Linux y subir el reporte.
2. Añadir un test de caracterización antes de cambiar la forma de respuesta de `GET /users`
   (el cambio es incompatible; convendría versionar la ruta o avisar a los consumidores).
3. Paginar en el repositorio en vez de en memoria cuando exista una base de datos real.
4. Añadir un check de review automático (Clase 4) sobre el PR.

## Aprendizajes sobre el uso de IA

- La calidad la decide el contexto y el patrón antes de generar, no el modelo.
- Verde no es probado: la IA genera tests rápido, pero hay que preguntar "¿qué mutación no
  detectaría este test?".
- El criterio de aceptar o rechazar propuestas (mutmut, validación en el service, endpoint
  nuevo) siguió siendo humano.

Evidencia: [BITACORA.md](../BITACORA.md), [docs/evidencia/](evidencia/), [CHANGELOG.md](../CHANGELOG.md).
