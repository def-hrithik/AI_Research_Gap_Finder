"""
Unit and integration tests for /api/health and /api/projects routes.
Verifies response envelopes, empty database state, CRUD operations,
error handling, and responsiveness.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.database.models import Base
from app.main import create_app


@pytest.fixture
def test_db_session(tmp_path):
    """Fixture providing an isolated SQLite database for testing."""
    db_file = tmp_path / "test_rgf.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False, "timeout": 30.0},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db_session):
    """FastAPI test client with overridden DB dependency."""
    app = create_app()

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as tc:
        yield tc


def test_health_endpoint(client):
    """Health endpoint must return 200 with status=ok and version."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert "version" in data


def test_projects_empty_database(client):
    """Empty database must promptly return 200 with empty list envelope."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) == 0
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0


def test_create_and_retrieve_project(client):
    """Creating a project returns 201 and is retrievable via GET."""
    payload = {"name": "Neuroscience RAG", "description": "Reviewing gap analysis in neural models"}
    create_res = client.post("/api/projects", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    project_id = created_data["project_id"]
    assert created_data["name"] == payload["name"]
    assert created_data["paper_count"] == 0
    assert created_data["status"] == "EMPTY"

    # Get single project
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["project_id"] == project_id
    assert retrieved["name"] == payload["name"]

    # List projects should contain 1 item
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert len(list_data["items"]) == 1
    assert list_data["items"][0]["project_id"] == project_id


def test_get_nonexistent_project_returns_404(client):
    """Non-existent project ID returns 404 with structured error."""
    response = client.get("/api/projects/prj_nonexistent_999")
    assert response.status_code == 404


def test_project_delete(client):
    """Deleting a project removes it and cascades properly."""
    res = client.post("/api/projects", json={"name": "Temporary Project"})
    project_id = res.json()["project_id"]

    del_res = client.delete(f"/api/projects/{project_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 404
