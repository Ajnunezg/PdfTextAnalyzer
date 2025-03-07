from PIL import Image
import os

class ImageProcessor:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png'}
        self.max_dimension = 2048  # Maximum dimension for either width or height

    def prepare_image(self, image_path):
        """
        Prepare image for OCR processing
        - Validate format
        - Resize if necessary
        - Optimize for OCR
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported image format: {file_ext}")

        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                # Resize if image is too large
                if max(img.size) > self.max_dimension:
                    ratio = self.max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Create temporary processed file
                temp_path = f"{os.path.splitext(image_path)[0]}_processed{file_ext}"
                img.save(temp_path, quality=95, optimize=True)

                return temp_path

        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
