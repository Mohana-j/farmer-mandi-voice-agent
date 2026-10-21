"""End-to-end API route tests."""

import pytest
from fastapi.testclient import TestClient


def test_health_and_config(client: TestClient):
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_config = client.get("/api/config")
    assert res_config.status_code == 200
    assert "data_provider_mode" in res_config.json()


def test_query_pipeline_and_evidence(client: TestClient):
    # 1. Create query
    create_payload = {
        "crop": "tomato",
        "grade": "Grade A",
        "location": "Dharmapuri",
        "radius_km": 50.0,
        "language": "en",
        "source_mode": "synthetic",
    }
    create_res = client.post("/api/queries", json=create_payload)
    assert create_res.status_code == 201
    q_data = create_res.json()
    query_id = q_data["query_id"]

    # 2. Run query pipeline
    run_res = client.post(f"/api/queries/{query_id}/run")
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["status"] == "completed"
    assert run_data["usable_records_count"] > 0

    # 3. Get results
    results_res = client.get(f"/api/queries/{query_id}/results")
    assert results_res.status_code == 200
    res_json = results_res.json()
    assert res_json["summary"]["usable_markets_count"] > 0
    assert "per kg" in res_json["summary"]["price_range_str"]
    assert len(res_json["voice_answer_en"]) > 0

    # 4. Get audit evidence
    evidence_res = client.get(f"/api/queries/{query_id}/evidence")
    assert evidence_res.status_code == 200
    ev_json = evidence_res.json()
    assert len(ev_json["tool_events"]) > 0
    assert len(ev_json["planning_steps"]) > 0
    assert len(ev_json["normalization_decisions"]) > 0


def test_action_preview_and_approval_idempotency(client: TestClient):
    # Setup query and run it
    q_res = client.post("/api/queries", json={"crop": "tomato", "location": "Dharmapuri"})
    q_id = q_res.json()["query_id"]
    client.post(f"/api/queries/{q_id}/run")

    # 1. Request preview
    preview_res = client.post("/api/actions/preview", json={
        "query_id": q_id,
        "action_type": "export_comparison",
        "payload": {}
    })
    assert preview_res.status_code == 200
    p_data = preview_res.json()
    action_id = p_data["action_id"]
    idem_key = p_data["idempotency_key"]

    # 2. Approve
    app_res = client.post(f"/api/actions/{action_id}/approve", json={
        "idempotency_key": idem_key,
        "approved": True
    })
    assert app_res.status_code == 200
    app_data = app_res.json()
    assert app_data["execution_status"] == "completed"
    assert app_data["verification_status"] == "verified_success"

    # 3. Repeat approve (Idempotency test)
    app_res_repeat = client.post(f"/api/actions/{action_id}/approve", json={
        "idempotency_key": idem_key,
        "approved": True
    })
    assert app_res_repeat.status_code == 200
    assert "Idempotent response" in app_res_repeat.json()["message"]


def test_official_tests_api(client: TestClient):
    # Test single run
    res_single = client.post("/api/tests/TC1/run")
    assert res_single.status_code == 200
    assert res_single.json()["status"] == "passed"

    # Test run all
    res_all = client.post("/api/tests/run-all")
    assert res_all.status_code == 200
    tests = res_all.json()
    assert len(tests) == 4
    for t in tests:
        assert t["status"] == "passed"
