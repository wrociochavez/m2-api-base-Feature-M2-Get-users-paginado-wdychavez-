"""Rutas HTTP del recurso `users`.

Patrón de referencia para nuevas rutas:
  - un `APIRouter` con `prefix` y `tags`
  - `response_model=` siempre; nunca devolver `dict` crudos
  - la función delega en `service.py` y no contiene lógica de negocio
  - los errores los levanta `service.py` con `core.errors`
"""
from fastapi import APIRouter, Query, status

from users import service
from users.schemas import User, UserCreate, UserPage

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserPage)
def list_users(
    q: str | None = Query(None, description="Busca en nombre o email"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Usuarios por página"),
    sort: str = Query("id", description="Campo de orden; `-` al inicio para descendente"),
) -> UserPage:
    return service.list_users(q=q, page=page, size=size, sort=sort)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    return service.get_user(user_id)


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate) -> User:
    return service.create_user(data)
