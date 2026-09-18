import io
import cv2
import numpy as np

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

def is_allowed_image(filename: str) -> bool:
    """Check if the filename has a supported image extension."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def analyze_image_quality(image_input, blur_threshold: float = 100.0, dark_threshold: float = 50.0, bright_threshold: float = 200.0) -> dict:
    """
    Perform basic image quality analysis using OpenCV:
    - Grayscale brightness calculation (mean pixel intensity)
    - Blur / sharpness calculation using Laplacian variance
    - Classification of brightness (Too Dark / Normal / Too Bright)
    - Classification of image quality (Blurry / Clear)

    :param image_input: FileStorage, bytes, io.BytesIO, or numpy array.
    :param blur_threshold: Variance threshold below which image is considered Blurry (default: 100.0).
    :param dark_threshold: Brightness threshold below which image is Too Dark (default: 50.0).
    :param bright_threshold: Brightness threshold above which image is Too Bright (default: 200.0).
    :return: dict with brightness, brightness_status, blur_score, quality_status
    """
    # 1. Convert input to OpenCV image (numpy array)
    if isinstance(image_input, np.ndarray):
        img = image_input
    else:
        # Handle FileStorage, BytesIO, or raw bytes
        if hasattr(image_input, "read"):
            data = image_input.read()
            # Reset pointer if possible
            if hasattr(image_input, "seek"):
                image_input.seek(0)
        elif isinstance(image_input, (bytes, bytearray)):
            data = image_input
        else:
            raise ValueError("Unsupported image input type.")

        if not data:
            raise ValueError("Empty image data provided.")

        np_arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img is None or img.size == 0:
        raise ValueError("Failed to decode image. File may be corrupted or not a valid image format.")

    # 2. Convert to grayscale
    if len(img.shape) == 2:
        gray = img
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Calculate brightness (mean intensity of grayscale image)
    brightness = float(np.mean(gray))

    if brightness < dark_threshold:
        brightness_status = "Too Dark"
    elif brightness > bright_threshold:
        brightness_status = "Too Bright"
    else:
        brightness_status = "Normal"

    # 4. Calculate blur/sharpness score using Laplacian variance
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    blur_score = laplacian_var

    if blur_score < blur_threshold:
        quality_status = "Blurry"
    else:
        quality_status = "Clear"

    return {
        "brightness": round(brightness, 2),
        "brightness_status": brightness_status,
        "blur_score": round(blur_score, 2),
        "quality_status": quality_status
    }
