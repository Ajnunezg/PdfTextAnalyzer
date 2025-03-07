import os
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from api_client import GeminiAPIClient
from image_processor import ImageProcessor
from date_extractor import extract_date
from utils import validate_image_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
api_client = GeminiAPIClient()
image_processor = ImageProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Validate file
        validate_image_file(filepath)

        # Process image
        processed_image = image_processor.prepare_image(filepath)

        # Get transcription
        transcription = api_client.transcribe_image(processed_image)

        # Extract date
        try:
            date_str = extract_date(transcription)
            output_filename = f"{date_str}.txt"
            date_found = True
        except ValueError:
            # Use the original filename (without extension) if date not found
            base_filename = os.path.splitext(filename)[0]
            output_filename = f"{base_filename}.txt"
            date_str = None
            date_found = False
        
        # Save transcription
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        with open(output_path, 'w') as f:
            f.write(transcription)

        return jsonify({
            'success': True,
            'transcription': transcription,
            'date': date_str,
            'output_file': output_filename,
            'date_found': date_found
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key as an environment variable")
        exit(1)

    app.run(host='0.0.0.0', port=5000)