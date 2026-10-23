"""Lógica de negocio del recurso `users`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).
"""
from core import errors
from users import repository
from users.schemas import User, UserCreate, UserPage


def get_user(user_id: int) -> User:
    user = repository.get(user_id)
    if user is None:
        raise errors.not_found("usuario", user_id)
    return user


def _sort_value(user: User, field: str) -> object:
    value = getattr(user, field)
    return value.lower() if isinstance(value, str) else value


def list_users(
    q: str | None = None,
    page: int = 1,
    size: int = 10,
    sort: str = "id",
) -> UserPage:
    """Lista usuarios con búsqueda, orden y paginación.

    Args:
        q: texto a buscar (sin distinguir mayúsculas) en `name` o `email`.
        page: número de página, empezando en 1.
        size: usuarios por página.
        sort: campo de orden; prefijo `-` para descendente.

    Returns:
        La página pedida con el total de coincidencias.

    Raises:
        HTTPException: 422 si `sort` no es un campo permitido.
    """
    users = repository.list_all()

    term = (q or "").strip().lower()
    if term:
        users = [u for u in users if term in u.name.lower() or term in u.email.lower()]

    descending = sort.startswith("-")
    field = sort[1:] if descending else sort
    if field not in ("id", "name", "email", "created_at"):
        raise errors.invalid_request(f"campo de orden no válido: {sort}")
    users = sorted(users, key=lambda u: (_sort_value(u, field), u.id), reverse=descending)

    total = len(users)
    pages = -(-total // size)
    start = (page - 1) * size
    return UserPage(
        items=users[start : start + size], total=total, page=page, size=size, pages=pages
    )


def create_user(data: UserCreate) -> User:
    if repository.find_by_email(str(data.email)) is not None:
        raise errors.already_exists("usuario", data.email)
    return repository.add(name=data.name, email=str(data.email))
