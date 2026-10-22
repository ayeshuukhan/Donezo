import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_task_repository
from app.main import app
from app.repository import InMemoryTaskRepository


@pytest.fixture()
def client():
    repo = InMemoryTaskRepository()  # har test ke liye fresh repo
    app.dependency_overrides[get_task_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def make(client, **kw):
    body = {"title": "Write tests", **kw}
    r = client.post("/tasks", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_task_defaults(client):
    t = make(client)
    assert t["id"] == 1
    assert t["status"] == "todo"
    assert t["priority"] == 3


def test_get_task(client):
    t = make(client)
    r = client.get(f"/tasks/{t['id']}")
    assert r.status_code == 200 and r.json()["title"] == "Write tests"


def test_list_and_filter_by_status(client):
    make(client, title="a")
    make(client, title="b", status="done")
    assert len(client.get("/tasks").json()) == 2
    done = client.get("/tasks", params={"status": "done"}).json()
    assert [t["title"] for t in done] == ["b"]


def test_list_pagination(client):
    for i in range(5):
        make(client, title=f"t{i}")
    r = client.get("/tasks", params={"limit": 2, "offset": 1}).json()
    assert [t["title"] for t in r] == ["t1", "t2"]


def test_patch_updates_only_sent_fields(client):
    t = make(client, description="keep me")
    r = client.patch(f"/tasks/{t['id']}", json={"status": "in_progress"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "in_progress"
    assert body["description"] == "keep me"
    assert body["updated_at"] >= t["updated_at"]


def test_patch_empty_body_is_400(client):
    t = make(client)
    assert client.patch(f"/tasks/{t['id']}", json={}).status_code == 400


def test_patch_null_title_is_422(client):
    t = make(client)
    assert client.patch(f"/tasks/{t['id']}", json={"title": None}).status_code == 422


def test_delete_then_404(client):
    t = make(client)
    assert client.delete(f"/tasks/{t['id']}").status_code == 204
    assert client.get(f"/tasks/{t['id']}").status_code == 404


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_task_404(client, method):
    kwargs = {"json": {"title": "x"}} if method == "patch" else {}
    assert getattr(client, method)("/tasks/999", **kwargs).status_code == 404


@pytest.mark.parametrize(
    "body",
    [
        {},                                  # title missing
        {"title": ""},                       # too short
        {"title": "x" * 121},                # too long
        {"title": "ok", "priority": 9},      # out of range
        {"title": "ok", "status": "bogus"},  # bad enum
        {"title": "ok", "extra": 1},         # unknown field
    ],
)
def test_invalid_create_is_422(client, body):
    assert client.post("/tasks", json=body).status_code == 422


def test_non_integer_id_is_422(client):
    assert client.get("/tasks/abc").status_code == 422
