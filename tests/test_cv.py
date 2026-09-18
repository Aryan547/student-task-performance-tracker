import io
import cv2
import numpy as np
import pytest
from cv_utils import is_allowed_image, analyze_image_quality

def create_test_image_bytes(pattern="checkerboard", width=100, height=100, ext="png"):
    """Generate in-memory image bytes for test cases."""
    if pattern == "black":
        img = np.zeros((height, width, 3), dtype=np.uint8)
    elif pattern == "white":
        img = np.full((height, width, 3), 255, dtype=np.uint8)
    elif pattern == "gray_uniform":
        img = np.full((height, width, 3), 128, dtype=np.uint8)
    elif pattern == "checkerboard":
        img = np.zeros((height, width, 3), dtype=np.uint8)
        # Create high-contrast alternating checkerboard squares for high Laplacian variance (sharp/clear)
        for i in range(0, height, 10):
            for j in range(0, width, 10):
                if ((i // 10) + (j // 10)) % 2 == 0:
                    img[i:i+10, j:j+10] = 200
                else:
                    img[i:i+10, j:j+10] = 50
    else:
        img = np.full((height, width, 3), 120, dtype=np.uint8)

    success, buffer = cv2.imencode(f".{ext}", img)
    assert success
    return buffer.tobytes()

def test_is_allowed_image():
    """Verify image extension validation logic."""
    assert is_allowed_image("photo.jpg") is True
    assert is_allowed_image("photo.jpeg") is True
    assert is_allowed_image("photo.png") is True
    assert is_allowed_image("photo.bmp") is True
    assert is_allowed_image("photo.webp") is True
    assert is_allowed_image("PHOTO.PNG") is True
    assert is_allowed_image("document.pdf") is False
    assert is_allowed_image("script.py") is False
    assert is_allowed_image("no_ext") is False
    assert is_allowed_image("") is False

def test_cv_utils_dark_image():
    """Verify detection of dark images."""
    data = create_test_image_bytes(pattern="black")
    result = analyze_image_quality(data)
    assert result["brightness"] == 0.0
    assert result["brightness_status"] == "Too Dark"

def test_cv_utils_bright_image():
    """Verify detection of over-exposed/bright images."""
    data = create_test_image_bytes(pattern="white")
    result = analyze_image_quality(data)
    assert result["brightness"] == 255.0
    assert result["brightness_status"] == "Too Bright"

def test_cv_utils_clear_and_blurry_images():
    """Verify sharpness and blur classification."""
    # Sharp checkerboard pattern
    sharp_data = create_test_image_bytes(pattern="checkerboard")
    sharp_result = analyze_image_quality(sharp_data)
    assert sharp_result["brightness_status"] == "Normal"
    assert sharp_result["quality_status"] == "Clear"
    assert sharp_result["blur_score"] > 100.0

    # Flat uniform image has 0 variance (blurry)
    flat_data = create_test_image_bytes(pattern="gray_uniform")
    flat_result = analyze_image_quality(flat_data)
    assert flat_result["brightness_status"] == "Normal"
    assert flat_result["quality_status"] == "Blurry"
    assert flat_result["blur_score"] < 100.0

def test_cv_utils_invalid_input():
    """Verify exception handling on invalid/corrupted bytes."""
    with pytest.raises(ValueError, match="Empty image data"):
        analyze_image_quality(b"")

    with pytest.raises(ValueError, match="Failed to decode image"):
        analyze_image_quality(b"not-an-image-data-stream")

def test_api_check_image_success(client):
    """Test POST /api/cv/check-image with valid multipart image upload."""
    image_bytes = create_test_image_bytes(pattern="checkerboard", ext="png")
    data = {
        "image": (io.BytesIO(image_bytes), "sample_assignment.png")
    }
    res = client.post("/api/cv/check-image", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert json_data["filename"] == "sample_assignment.png"
    assert "brightness" in json_data
    assert "brightness_status" in json_data
    assert "blur_score" in json_data
    assert "quality_status" in json_data
    assert json_data["quality_status"] == "Clear"

def test_api_check_image_missing_file(client):
    """Test POST /api/cv/check-image with missing file payload."""
    res = client.post("/api/cv/check-image", data={}, content_type="multipart/form-data")
    assert res.status_code == 400
    assert "No image file provided" in res.get_json()["error"]

def test_api_check_image_unsupported_format(client):
    """Test POST /api/cv/check-image with unsupported file format."""
    data = {
        "image": (io.BytesIO(b"dummy pdf content"), "assignment.pdf")
    }
    res = client.post("/api/cv/check-image", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert "Unsupported file format" in res.get_json()["error"]

def test_api_check_image_corrupted_file(client):
    """Test POST /api/cv/check-image with corrupted image content."""
    data = {
        "image": (io.BytesIO(b"corrupted image binary header"), "corrupted.jpg")
    }
    res = client.post("/api/cv/check-image", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert "Failed to decode image" in res.get_json()["error"]
