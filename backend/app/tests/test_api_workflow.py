from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ["SACB_DATABASE_URL"] = f"sqlite+pysqlite:///{Path(tempfile.mkdtemp()) / 'sacb-test.db'}"
os.environ["SACB_EVIDENCE_STORAGE_PATH"] = str(Path(tempfile.mkdtemp()) / "evidence")
os.environ["SACB_JWT_SECRET"] = "test-secret"
os.environ["SACB_SEED_ADMIN_EMAIL"] = "admin@example.com"
os.environ["SACB_SEED_ADMIN_PASSWORD"] = "ChangeMe123!"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SAMPLE = ROOT / "sample_data"


def auth_headers(
    client: TestClient, email: str = "admin@example.com", password: str = "ChangeMe123!"
) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_case_alert_to_report_workflow() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        created = client.post(
            "/cases",
            json={
                "title": "Suspicious PowerShell",
                "description": "Endpoint alert triage",
                "severity": "High",
                "source_system": "Sophos",
            },
            headers=headers,
        )
        assert created.status_code == 200, created.text
        case_id = created.json()["id"]

        raw = (SAMPLE / "sophos_endpoint_apcviolation.txt").read_text()
        alert = client.post(
            f"/cases/{case_id}/alerts/paste",
            json={"raw_content": raw, "source_system": "Sophos"},
            headers=headers,
        )
        assert alert.status_code == 200, alert.text
        assert alert.json()["alert_type"] == "sophos_endpoint"

        iocs = client.get(f"/cases/{case_id}/iocs", headers=headers)
        assert iocs.status_code == 200
        assert any(item["type"] == "sha256" for item in iocs.json())

        timeline = client.get(f"/cases/{case_id}/timeline", headers=headers)
        assert timeline.status_code == 200
        assert len(timeline.json()) >= 1

        tasks = client.get(f"/cases/{case_id}/tasks", headers=headers)
        assert tasks.status_code == 200
        assert any("process tree" in item["title"].lower() for item in tasks.json())

        mappings = client.post(f"/cases/{case_id}/mitre/suggest", headers=headers)
        assert mappings.status_code == 200, mappings.text
        assert any(item["technique"]["technique_id"] == "T1059.001" for item in mappings.json())

        report = client.post(
            f"/cases/{case_id}/reports/generate",
            json={"report_type": "analyst", "format": "markdown"},
            headers=headers,
        )
        assert report.status_code == 200, report.text
        assert "Extracted IOCs" in report.json()["content"]

        audit = client.get(f"/cases/{case_id}/audit", headers=headers)
        assert audit.status_code == 200
        actions = {item["action"] for item in audit.json()}
        assert {"case.created", "alert.uploaded", "mitre.suggested", "report.generated"}.issubset(
            actions
        )


def test_rbac_blocks_viewer_from_mutating_cases() -> None:
    with TestClient(app) as client:
        admin_headers = auth_headers(client)
        response = client.post(
            "/users",
            json={
                "email": "viewer@example.com",
                "display_name": "Viewer",
                "password": "ViewerPass123!",
                "role": "Viewer",
            },
            headers=admin_headers,
        )
        assert response.status_code in {200, 409}
        viewer_headers = auth_headers(client, "viewer@example.com", "ViewerPass123!")
        denied = client.post(
            "/cases",
            json={"title": "Viewer attempt", "description": "Should fail"},
            headers=viewer_headers,
        )
        assert denied.status_code == 403


def test_file_upload_validation_rejects_unsupported_evidence() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        created = client.post(
            "/cases", json={"title": "Evidence validation", "description": ""}, headers=headers
        )
        case_id = created.json()["id"]
        response = client.post(
            f"/cases/{case_id}/evidence",
            files={"file": ("tool.exe", b"MZ fake binary", "application/octet-stream")},
            headers=headers,
        )
        assert response.status_code == 400
