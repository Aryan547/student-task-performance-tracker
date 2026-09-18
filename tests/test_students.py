import json
import pytest

def test_student_creation(client):
    """Test creating a valid student."""
    response = client.post("/api/students", json={
        "name": "Aarav Sharma",
        "roll_number": "21BCE1001",
        "course": "B.Tech CSE",
        "semester": 6,
        "email": "aarav.sharma@example.com"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "student_id" in data
    assert data["student_id"] > 0

def test_student_retrieval(client):
    """Test retrieving student list and specific student details."""
    # Seed a student
    create_res = client.post("/api/students", json={
        "name": "Diya Patel",
        "roll_number": "21BCE1002",
        "course": "B.Tech IT",
        "semester": 6,
        "email": "diya.patel@example.com"
    })
    student_id = create_res.get_json()["student_id"]

    # Test list
    list_res = client.get("/api/students")
    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data["success"] is True
    assert list_data["count"] >= 1
    assert any(s["student_id"] == student_id for s in list_data["students"])

    # Test get by ID
    get_res = client.get(f"/api/students/{student_id}")
    assert get_res.status_code == 200
    get_data = get_res.get_json()
    assert get_data["success"] is True
    assert get_data["student"]["roll_number"] == "21BCE1002"
    assert get_data["student"]["name"] == "Diya Patel"

def test_student_update(client):
    """Test updating existing student details."""
    create_res = client.post("/api/students", json={
        "name": "Rohan Gupta",
        "roll_number": "21BCE1003",
        "course": "B.Tech ECE",
        "semester": 5,
        "email": "rohan.gupta@example.com"
    })
    student_id = create_res.get_json()["student_id"]

    # Update student
    update_res = client.put(f"/api/students/{student_id}", json={
        "name": "Rohan S. Gupta",
        "roll_number": "21BCE1003",
        "course": "B.Tech ECE (Honors)",
        "semester": 6,
        "email": "rohan.s.gupta@example.com"
    })
    assert update_res.status_code == 200
    update_data = update_res.get_json()
    assert update_data["success"] is True
    assert update_data["student"]["name"] == "Rohan S. Gupta"
    assert update_data["student"]["semester"] == 6
    assert update_data["student"]["email"] == "rohan.s.gupta@example.com"

def test_student_deletion(client):
    """Test deleting a student and cascading task deletion."""
    create_res = client.post("/api/students", json={
        "name": "Ananya Verma",
        "roll_number": "21BCE1004",
        "course": "B.Tech CSE",
        "semester": 6,
        "email": "ananya.verma@example.com"
    })
    student_id = create_res.get_json()["student_id"]

    # Assign a task to the student
    task_res = client.post("/api/tasks", json={
        "student_id": student_id,
        "title": "OS Project Report",
        "description": "Submit final report",
        "deadline": "2026-10-15",
        "status": "Pending"
    })
    assert task_res.status_code == 201
    task_id = task_res.get_json()["task_id"]

    # Delete the student
    del_res = client.delete(f"/api/students/{student_id}")
    assert del_res.status_code == 200
    del_data = del_res.get_json()
    assert del_data["success"] is True

    # Student should now be not found
    get_res = client.get(f"/api/students/{student_id}")
    assert get_res.status_code == 404

    # The linked task should be deleted by cascade
    task_get_res = client.get(f"/api/tasks/{task_id}")
    assert task_get_res.status_code == 404

def test_student_invalid_inputs(client):
    """Test validation errors on missing and invalid student inputs."""
    # Missing name
    res = client.post("/api/students", json={
        "name": "",
        "roll_number": "21BCE1005",
        "course": "B.Tech",
        "semester": 4,
        "email": "test@example.com"
    })
    assert res.status_code == 400
    assert "name" in res.get_json()["error"].lower()

    # Missing roll number
    res = client.post("/api/students", json={
        "name": "Valid Name",
        "roll_number": "",
        "course": "B.Tech",
        "semester": 4,
        "email": "test@example.com"
    })
    assert res.status_code == 400
    assert "roll" in res.get_json()["error"].lower()

    # Invalid semester (< 1)
    res = client.post("/api/students", json={
        "name": "Valid Name",
        "roll_number": "21BCE1006",
        "course": "B.Tech",
        "semester": 0,
        "email": "test6@example.com"
    })
    assert res.status_code == 400
    assert "semester" in res.get_json()["error"].lower()

    # Invalid semester (> 8)
    res = client.post("/api/students", json={
        "name": "Valid Name",
        "roll_number": "21BCE1007",
        "course": "B.Tech",
        "semester": 9,
        "email": "test7@example.com"
    })
    assert res.status_code == 400
    assert "semester" in res.get_json()["error"].lower()

    # Invalid email format
    res = client.post("/api/students", json={
        "name": "Valid Name",
        "roll_number": "21BCE1008",
        "course": "B.Tech",
        "semester": 4,
        "email": "invalid-email-address"
    })
    assert res.status_code == 400
    assert "email" in res.get_json()["error"].lower()

def test_student_duplicate_constraints(client):
    """Test duplicate roll number and duplicate email conflicts."""
    client.post("/api/students", json={
        "name": "Original Student",
        "roll_number": "21BCE1010",
        "course": "B.Tech",
        "semester": 4,
        "email": "unique@example.com"
    })

    # Duplicate roll number
    res_roll = client.post("/api/students", json={
        "name": "Second Student",
        "roll_number": "21BCE1010",
        "course": "B.Tech",
        "semester": 4,
        "email": "unique2@example.com"
    })
    assert res_roll.status_code == 409
    assert "already exists" in res_roll.get_json()["error"]

    # Duplicate email
    res_email = client.post("/api/students", json={
        "name": "Third Student",
        "roll_number": "21BCE1011",
        "course": "B.Tech",
        "semester": 4,
        "email": "unique@example.com"
    })
    assert res_email.status_code == 409
    assert "already exists" in res_email.get_json()["error"]
