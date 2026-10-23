"""Tests del listado `GET /users` con búsqueda, orden y paginación.

Datos semilla (id: nombre / email): 1 Ada Lovelace, 2 Alan Turing, 3 Grace Hopper,
4 Katherine Johnson. Mismo estilo que `test_users.py`.
"""
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from users import repository, service
from users.schemas import User


def _ids(response) -> list[int]:
    return [u["id"] for u in response.json()["items"]]


# --- Estructura y paginación -------------------------------------------------


def test_list_users_estructura_de_la_pagina(client: TestClient) -> None:
    response = client.get("/users")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "page", "size", "pages"}
    assert (body["total"], body["page"], body["size"], body["pages"]) == (4, 1, 10, 1)


def test_list_users_pagina_1_con_size_2(client: TestClient) -> None:
    response = client.get("/users", params={"page": 1, "size": 2})

    assert _ids(response) == [1, 2]
    assert response.json()["pages"] == 2


def test_list_users_pagina_2_con_size_2(client: TestClient) -> None:
    response = client.get("/users", params={"page": 2, "size": 2})

    assert _ids(response) == [3, 4]


def test_list_users_ultima_pagina_parcial(client: TestClient) -> None:
    response = client.get("/users", params={"page": 2, "size": 3})

    assert _ids(response) == [4]
    assert response.json()["pages"] == 2


def test_list_users_pagina_fuera_de_rango_devuelve_items_vacios(client: TestClient) -> None:
    response = client.get("/users", params={"page": 99, "size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 4


def test_list_users_size_maximo_100_es_valido(client: TestClient) -> None:
    response = client.get("/users", params={"size": 100})

    assert response.status_code == 200


@pytest.mark.parametrize(
    "params",
    [{"page": 0}, {"page": -1}, {"size": 0}, {"size": 101}, {"page": "abc"}],
)
def test_list_users_page_o_size_fuera_de_rango_devuelve_422(
    client: TestClient, params: dict
) -> None:
    response = client.get("/users", params=params)

    assert response.status_code == 422


# --- Búsqueda ----------------------------------------------------------------


def test_list_users_busca_por_nombre_sin_distinguir_mayusculas(client: TestClient) -> None:
    response = client.get("/users", params={"q": "ADA"})

    assert _ids(response) == [1]


def test_list_users_busca_por_email(client: TestClient) -> None:
    response = client.get("/users", params={"q": "grace@"})

    assert _ids(response) == [3]


def test_list_users_busca_por_substring(client: TestClient) -> None:
    # "lan" solo está en "Alan Turing" / alan@example.com.
    response = client.get("/users", params={"q": "lan"})

    assert _ids(response) == [2]
    assert response.json()["total"] == 1


def test_list_users_q_sin_coincidencias_devuelve_pagina_vacia(client: TestClient) -> None:
    response = client.get("/users", params={"q": "zzz"})

    assert response.status_code == 200
    body = response.json()
    assert (body["items"], body["total"], body["pages"]) == ([], 0, 0)


def test_list_users_q_vacio_o_solo_espacios_no_filtra(client: TestClient) -> None:
    vacio = client.get("/users", params={"q": ""})
    espacios = client.get("/users", params={"q": "   "})

    assert vacio.json()["total"] == 4
    assert espacios.json()["total"] == 4


def test_list_users_q_se_recorta_antes_de_buscar(client: TestClient) -> None:
    response = client.get("/users", params={"q": "  turing "})

    assert _ids(response) == [2]


def test_list_users_busqueda_se_combina_con_paginacion(client: TestClient) -> None:
    # "example.com" está en los 4 emails; el total refleja el filtro, no la página.
    response = client.get("/users", params={"q": "example.com", "size": 3})

    body = response.json()
    assert body["total"] == 4
    assert len(body["items"]) == 3
    assert body["pages"] == 2


# --- Orden -------------------------------------------------------------------


def test_list_users_orden_por_defecto_es_id_ascendente(client: TestClient) -> None:
    response = client.get("/users")

    assert _ids(response) == [1, 2, 3, 4]


def test_list_users_orden_por_nombre_descendente(client: TestClient) -> None:
    response = client.get("/users", params={"sort": "-name"})

    assert _ids(response) == [4, 3, 2, 1]


def test_list_users_orden_por_email_ascendente(client: TestClient) -> None:
    client.post("/users", json={"name": "Zed", "email": "aaa@example.com"})

    response = client.get("/users", params={"sort": "email"})

    assert _ids(response)[0] == 5


def test_list_users_orden_por_created_at_descendente(client: TestClient) -> None:
    client.post("/users", json={"name": "Zoe", "email": "zoe@example.com"})

    response = client.get("/users", params={"sort": "-created_at"})

    assert _ids(response)[0] == 5  # el más reciente primero


def test_list_users_orden_ignora_mayusculas(client: TestClient) -> None:
    client.post("/users", json={"name": "alicia", "email": "alicia@example.com"})

    response = client.get("/users", params={"sort": "name"})

    # "alicia" (minúscula) va entre "Alan" y "Grace", no al final.
    assert _ids(response) == [1, 2, 5, 3, 4]


def test_list_users_orden_con_paginacion_es_estable(client: TestClient) -> None:
    pagina1 = client.get("/users", params={"sort": "-name", "size": 2, "page": 1})
    pagina2 = client.get("/users", params={"sort": "-name", "size": 2, "page": 2})

    assert _ids(pagina1) + _ids(pagina2) == [4, 3, 2, 1]


@pytest.mark.parametrize("sort", ["password", "-", "", "name,id", "-ID"])
def test_list_users_sort_invalido_devuelve_422(client: TestClient, sort: str) -> None:
    response = client.get("/users", params={"sort": sort})

    assert response.status_code == 422
    assert "orden" in response.json()["detail"]


# --- Idempotencia y no mutación ----------------------------------------------


def test_list_users_es_idempotente(client: TestClient) -> None:
    params = {"q": "a", "page": 1, "size": 2, "sort": "-name"}

    primera = client.get("/users", params=params)
    segunda = client.get("/users", params=params)

    assert primera.json() == segunda.json()


def test_list_users_no_modifica_el_almacen(client: TestClient) -> None:
    antes = [u.id for u in repository.list_all()]

    client.get("/users", params={"sort": "-name", "size": 1})

    assert [u.id for u in repository.list_all()] == antes


# --- Unitarios del service (repositorio simulado) ----------------------------


def test_service_list_users_usa_el_repositorio_y_calcula_paginas(monkeypatch) -> None:
    ahora = datetime.now(timezone.utc)
    usuarios = [
        User(id=i, name=f"U{i}", email=f"u{i}@x.com", created_at=ahora) for i in range(1, 8)
    ]
    monkeypatch.setattr(repository, "list_all", lambda: usuarios)

    page = service.list_users(size=3, page=3)

    assert (page.total, page.pages) == (7, 3)
    assert [u.id for u in page.items] == [7]
