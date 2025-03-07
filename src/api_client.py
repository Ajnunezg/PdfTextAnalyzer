import os
import google.generativeai as genai
from PIL import Image

class GeminiAPIClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')

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
