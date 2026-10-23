"""Integración de punta a punta: crear usuarios por la API y consultarlos en el listado."""
from fastapi.testclient import TestClient


def _crear(client: TestClient, name: str, email: str) -> int:
    response = client.post("/users", json={"name": name, "email": email})
    assert response.status_code == 201
    return response.json()["id"]


def test_flujo_crear_buscar_ordenar_y_paginar(client: TestClient) -> None:
    ids = [
        _crear(client, "Barbara Liskov", "barbara@dev.org"),
        _crear(client, "Barbara McClintock", "bmc@dev.org"),
        _crear(client, "Bjarne Stroustrup", "bjarne@dev.org"),
    ]

    pagina1 = client.get("/users", params={"q": "dev.org", "sort": "-name", "size": 2})
    pagina2 = client.get("/users", params={"q": "dev.org", "sort": "-name", "size": 2, "page": 2})

    assert pagina1.status_code == 200
    assert pagina1.json()["total"] == 3
    assert [u["id"] for u in pagina1.json()["items"]] == [ids[2], ids[1]]
    assert [u["id"] for u in pagina2.json()["items"]] == [ids[0]]


def test_usuario_creado_aparece_en_el_total_del_listado(client: TestClient) -> None:
    antes = client.get("/users").json()["total"]

    _crear(client, "Nuevo Usuario", "nuevo@dev.org")

    assert client.get("/users").json()["total"] == antes + 1


def test_listado_y_detalle_son_consistentes(client: TestClient) -> None:
    item = client.get("/users", params={"q": "ada"}).json()["items"][0]

    detalle = client.get(f"/users/{item['id']}")

    assert detalle.json() == item


def test_health_responde_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
