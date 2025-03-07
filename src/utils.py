import os
from PIL import Image

def validate_image_file(file_path):
    """
    Validate that the file is a supported image file
    """
    if not os.path.exists(file_path):
        raise ValueError("File does not exist")

    # Check file extension
    valid_extensions = {'.jpg', '.jpeg', '.png'}
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext not in valid_extensions:
        raise ValueError(f"Unsupported file format. Supported formats: {', '.join(valid_extensions)}")

    # Try opening the image to verify it's valid
    try:
        with Image.open(file_path) as img:
            img.verify()
    except Exception:
        raise ValueError("Invalid or corrupted image file")

    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if os.path.getsize(file_path) > max_size:
        raise ValueError("Image file is too large (maximum size: 10MB)")

    return True
