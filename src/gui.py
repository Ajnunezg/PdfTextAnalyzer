import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
from api_client import GeminiAPIClient
from image_processor import ImageProcessor
from date_extractor import extract_date
from utils import validate_image_file

class JournalTranscriberApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Journal Entry Transcriber")
        self.geometry("800x600")
        
        self.api_client = GeminiAPIClient()
        self.image_processor = ImageProcessor()
        
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        # File selection frame
        self.file_frame = ttk.LabelFrame(self, text="File Selection")
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, width=50)
        self.browse_button = ttk.Button(self.file_frame, text="Browse", command=self._browse_file)

        # Preview frame
        self.preview_frame = ttk.LabelFrame(self, text="Image Preview")
        self.preview_label = ttk.Label(self.preview_frame)

        # Progress frame
        self.progress_frame = ttk.LabelFrame(self, text="Progress")
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(self.progress_frame, textvariable=self.progress_var)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')

        # Action buttons
        self.transcribe_button = ttk.Button(self, text="Transcribe", command=self._transcribe_image)
        self.transcribe_button.state(['disabled'])

    def _setup_layout(self):
        # File selection layout
        self.file_frame.pack(fill='x', padx=10, pady=5)
        self.file_path_entry.pack(side='left', padx=5, pady=5)
        self.browse_button.pack(side='left', padx=5, pady=5)

        # Preview layout
        self.preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.preview_label.pack(padx=5, pady=5)

        # Progress layout
        self.progress_frame.pack(fill='x', padx=10, pady=5)
        self.progress_label.pack(padx=5, pady=2)
        self.progress_bar.pack(fill='x', padx=5, pady=2)

        # Action buttons layout
        self.transcribe_button.pack(pady=10)

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            try:
                validate_image_file(file_path)
                self.file_path_var.set(file_path)
                self._update_preview(file_path)
                self.transcribe_button.state(['!disabled'])
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _update_preview(self, file_path):
        # Load and resize image for preview
        image = Image.open(file_path)
        # Maintain aspect ratio
        display_size = (300, 300)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        
        self.preview_label.configure(image=photo)
        self.preview_label.image = photo  # Keep a reference

    def _transcribe_image(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an image file first")
            return

        self.progress_bar.start()
        self.progress_var.set("Processing image...")
        self.transcribe_button.state(['disabled'])

        try:
            # Process image
            processed_image = self.image_processor.prepare_image(file_path)
            
            # Get transcription from API
            transcription = self.api_client.transcribe_image(processed_image)
            
            # Extract date from transcription
            date_str = extract_date(transcription)
            
            # Save transcription
            output_filename = f"{date_str}.txt"
            output_path = os.path.join(os.path.dirname(file_path), output_filename)
            
            with open(output_path, 'w') as f:
                f.write(transcription)
            
            self.progress_var.set(f"Transcription saved to: {output_filename}")
            messagebox.showinfo("Success", f"Transcription completed and saved to {output_filename}")
            
        except Exception as e:
            self.progress_var.set("Error occurred during transcription")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.progress_bar.stop()
            self.transcribe_button.state(['!disabled'])
