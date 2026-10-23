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
    raise NotImplementedError


def create_user(data: UserCreate) -> User:
    if repository.find_by_email(str(data.email)) is not None:
        raise errors.already_exists("usuario", data.email)
    return repository.add(name=data.name, email=str(data.email))
