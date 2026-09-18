import pytest

def test_dashboard_stats_empty_db(client):
    """Test dashboard statistics when no records exist."""
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    stats = data["stats"]
    assert stats["total_students"] == 0
    assert stats["total_tasks"] == 0
    assert stats["completed_tasks"] == 0
    assert stats["pending_tasks"] == 0
    assert stats["completion_percentage"] == 0.0
    assert stats["student_performance"] == []

def test_dashboard_stats_calculation(client):
    """Test dashboard metric calculations with students and mixed task statuses."""
    # Create Student A
    res_a = client.post("/api/students", json={
        "name": "Arjun Rao",
        "roll_number": "21BCE3001",
        "course": "B.Tech CSE",
        "semester": 6,
        "email": "arjun.rao@example.com"
    })
    student_a_id = res_a.get_json()["student_id"]

    # Create Student B
    res_b = client.post("/api/students", json={
        "name": "Bhavna Jain",
        "roll_number": "21BCE3002",
        "course": "B.Tech IT",
        "semester": 6,
        "email": "bhavna.jain@example.com"
    })
    student_b_id = res_b.get_json()["student_id"]

    # Student A: 2 Completed tasks, 1 Pending task
    client.post("/api/tasks", json={
        "student_id": student_a_id,
        "title": "Task A1",
        "deadline": "2026-10-01",
        "status": "Completed"
    })
    client.post("/api/tasks", json={
        "student_id": student_a_id,
        "title": "Task A2",
        "deadline": "2026-10-05",
        "status": "Completed"
    })
    client.post("/api/tasks", json={
        "student_id": student_a_id,
        "title": "Task A3",
        "deadline": "2026-10-10",
        "status": "Pending"
    })

    # Student B: 1 Pending task
    client.post("/api/tasks", json={
        "student_id": student_b_id,
        "title": "Task B1",
        "deadline": "2026-10-12",
        "status": "Pending"
    })

    # Fetch stats via GET /api/dashboard/stats
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    stats = data["stats"]

    # Verify counts
    assert stats["total_students"] == 2
    assert stats["total_tasks"] == 4
    assert stats["completed_tasks"] == 2
    assert stats["pending_tasks"] == 2

    # Verify completion percentage: 2 / 4 * 100 = 50.0%
    assert stats["completion_percentage"] == 50.0

    # Verify student breakdown
    perf = stats["student_performance"]
    assert len(perf) == 2

    perf_a = next(s for s in perf if s["student_id"] == student_a_id)
    assert perf_a["total_assigned"] == 3
    assert perf_a["total_completed"] == 2
    assert perf_a["total_pending"] == 1
    assert perf_a["completion_rate"] == 66.7

    perf_b = next(s for s in perf if s["student_id"] == student_b_id)
    assert perf_b["total_assigned"] == 1
    assert perf_b["total_completed"] == 0
    assert perf_b["total_pending"] == 1
    assert perf_b["completion_rate"] == 0.0

def test_view_routes_render_success(client):
    """Verify all 4 core frontend HTML routes return 200 OK."""
    assert client.get("/").status_code == 200
    assert client.get("/students").status_code == 200
    assert client.get("/tasks").status_code == 200
    assert client.get("/dashboard").status_code == 200
