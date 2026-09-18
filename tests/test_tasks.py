import pytest

@pytest.fixture
def sample_student(client):
    """Helper fixture to create a student for task assignment."""
    res = client.post("/api/students", json={
        "name": "Kavya Nair",
        "roll_number": "21BCE2001",
        "course": "B.Tech CSE",
        "semester": 6,
        "email": "kavya.nair@example.com"
    })
    return res.get_json()["student_id"]

def test_task_creation(client, sample_student):
    """Test creating a valid task."""
    res = client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Data Structures Assignment 1",
        "description": "Implement AVL Tree balancing algorithms",
        "deadline": "2026-10-20",
        "status": "Pending"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert "task_id" in data
    assert data["task_id"] > 0

def test_task_completion(client, sample_student):
    """Test marking a task as completed."""
    create_res = client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Mini Project Presentation",
        "description": "Prepare 10 slide deck",
        "deadline": "2026-11-01",
        "status": "Pending"
    })
    task_id = create_res.get_json()["task_id"]

    # Mark as completed
    patch_res = client.patch(f"/api/tasks/{task_id}/complete")
    assert patch_res.status_code == 200
    patch_data = patch_res.get_json()
    assert patch_data["success"] is True
    assert patch_data["status"] == "Completed"

    # Verify task status is indeed Completed
    get_res = client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["task"]["status"] == "Completed"

def test_task_deletion(client, sample_student):
    """Test deleting a task."""
    create_res = client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Draft Essay",
        "description": "Short essay",
        "deadline": "2026-10-30",
        "status": "Pending"
    })
    task_id = create_res.get_json()["task_id"]

    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["success"] is True

    # Check 404
    get_res = client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 404

def test_task_filtering_by_status(client, sample_student):
    """Test filtering tasks by Pending and Completed status."""
    # Create 2 pending tasks
    client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Pending Task 1",
        "deadline": "2026-10-15",
        "status": "Pending"
    })
    client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Pending Task 2",
        "deadline": "2026-10-16",
        "status": "Pending"
    })

    # Create 1 completed task
    client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Completed Task 1",
        "deadline": "2026-10-10",
        "status": "Completed"
    })

    # Filter: All
    all_res = client.get("/api/tasks")
    assert all_res.status_code == 200
    assert all_res.get_json()["count"] == 3

    # Filter: Pending
    pending_res = client.get("/api/tasks?status=Pending")
    assert pending_res.status_code == 200
    pending_tasks = pending_res.get_json()["tasks"]
    assert len(pending_tasks) == 2
    assert all(t["status"] == "Pending" for t in pending_tasks)

    # Filter: Completed
    completed_res = client.get("/api/tasks?status=Completed")
    assert completed_res.status_code == 200
    completed_tasks = completed_res.get_json()["tasks"]
    assert len(completed_tasks) == 1
    assert all(t["status"] == "Completed" for t in completed_tasks)

def test_task_invalid_inputs(client, sample_student):
    """Test task validation failure scenarios."""
    # Non-existent student ID
    res = client.post("/api/tasks", json={
        "student_id": 99999,
        "title": "Invalid Student Task",
        "deadline": "2026-10-25"
    })
    assert res.status_code == 404
    assert "does not exist" in res.get_json()["error"]

    # Missing title
    res_title = client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "   ",
        "deadline": "2026-10-25"
    })
    assert res_title.status_code == 400
    assert "title" in res_title.get_json()["error"].lower()

    # Invalid deadline format
    res_deadline = client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Bad Date Task",
        "deadline": "25-10-2026"  # wrong format, should be YYYY-MM-DD
    })
    assert res_deadline.status_code == 400
    assert "yyyy-mm-dd" in res_deadline.get_json()["error"].lower()

    # Invalid status
    res_status = client.post("/api/tasks", json={
        "student_id": sample_student,
        "title": "Bad Status Task",
        "deadline": "2026-10-25",
        "status": "In-Progress"
    })
    assert res_status.status_code == 400
    assert "status" in res_status.get_json()["error"].lower()
