import os
import google.generativeai as genai
from PIL import Image
import getpass  # Import the getpass module

class GeminiAPIClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Prompt the user for the API key
            api_key = getpass.getpass("Enter your Gemini API key: ")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not provided")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def transcribe_image(self, image_path):
        """
        Transcribe handwritten text from an image using Gemini API

        Args:
            image_path: Path to the image file

        Returns:
            str: Transcribed text
        """
        try:
            image = Image.open(image_path)

            prompt = """
            Please transcribe the handwritten text in this journal entry image.
            Focus on accurate text transcription and maintain the original formatting.
            Include any dates that appear in the text.
            """

            response = self.model.generate_content([prompt, image])

            if response.text:
                return response.text.strip()
            else:
                raise ValueError("No text was transcribed from the image")

        except Exception as e:
            raise Exception(f"API transcription error: {str(e)}")