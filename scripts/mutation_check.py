"""Mutation testing manual para `users/service.py` (mutmut no corre en Windows nativo).

Aplica una mutación a la vez (un bug a propósito), corre la suite y restaura el
archivo. Mutante muerto = algún test falla; vivo = la suite sigue en verde.

Uso:  python scripts/mutation_check.py          (desde la raíz del repo)
"""
import subprocess
import sys
from pathlib import Path

TARGET = Path("users/service.py")

# (descripción, texto original, texto mutado) — cada `original` aparece una sola vez.
MUTATIONS = [
    ("búsqueda: `or` -> `and`", "term in u.name.lower() or term in u.email.lower()",
     "term in u.name.lower() and term in u.email.lower()"),
    ("búsqueda: no buscar en nombre", "term in u.name.lower() or", "False or"),
    ("búsqueda: no recortar espacios", '(q or "").strip().lower()', '(q or "").lower()'),
    ("búsqueda: no ignorar mayúsculas", '(q or "").strip().lower()', '(q or "").strip()'),
    ("búsqueda: q vacío ya no devuelve todo", "if not term:", "if term:"),
    ("orden: invertir dirección", 'descending = sort.startswith("-")',
     'descending = not sort.startswith("-")'),
    ("orden: no quitar el prefijo '-'", 'sort.removeprefix("-")', "sort"),
    ("orden: campo inválido aceptado", "if field not in SORT_FIELDS:", "if field in SORT_FIELDS:"),
    ("orden: quitar campo email", '"name", "email", "created_at")',
     '"name", "created_at")'),
    ("orden: sin desempate por id", "(_sort_value(u, field), u.id)", "(_sort_value(u, field),)"),
    ("orden: distinguir mayúsculas", "value.lower() if isinstance(value, str) else value",
     "value"),
    ("paginación: off-by-one en offset", "start = (page - 1) * size", "start = page * size"),
    ("paginación: página de size+1", "users[start : start + size]",
     "users[start : start + size + 1]"),
    ("paginación: pages sin redondeo hacia arriba", "-(-total // size)", "total // size"),
    ("paginación: total tras recortar", "total = len(users)", "total = len(users[:1])"),
]


def run_suite() -> bool:
    """True si la suite pasa (mutante vivo)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def main() -> int:
    original = TARGET.read_bytes().decode("utf-8")
    crlf = "\r\n" in original
    base = original.replace("\r\n", "\n")
    if not run_suite():
        print("La suite no pasa sin mutar; abortando.")
        return 2
    survivors = []
    try:
        for desc, old, new in MUTATIONS:
            if base.count(old) != 1:
                print(f"OMITIDA  {desc} (patrón aparece {base.count(old)} veces)")
                continue
            mutated = base.replace(old, new)
            TARGET.write_text(mutated.replace("\n", "\r\n") if crlf else mutated,
                              encoding="utf-8", newline="")
            alive = run_suite()
            print(f"{'VIVO  ' if alive else 'MUERTO'}  {desc}")
            if alive:
                survivors.append(desc)
    finally:
        TARGET.write_bytes(original.encode("utf-8"))
    total = len(MUTATIONS)
    print(f"\nMutantes: {total}  muertos: {total - len(survivors)}  vivos: {len(survivors)}")
    print(f"Mutation score: {100 * (total - len(survivors)) / total:.0f}%")
    return 1 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
