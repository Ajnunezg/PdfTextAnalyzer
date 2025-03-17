import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
from api_client import GeminiAPIClient
from image_processor import ImageProcessor
from date_extractor import extract_date
from utils import validate_image_file

class JournalTranscriberApp:
    def __init__(self):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Journal Entry Transcriber")
        self.root.geometry("800x600")

        self._apply_theme()  # Apply custom theme

        self.api_key = ""
        self.api_client = None
        self.image_processor = ImageProcessor()

        self._create_widgets()
        self._setup_layout()

    def _apply_theme(self):
        # Create a style
        self.style = ttk.Style(self.root)

        # Configure steel and orange theme
        self.root.tk.call("source", "sun_valley/sun-valley.tcl")
        self.style.theme_use("sun-valley-dark")
        self.style.configure("TButton", foreground="#FFFFFF", background="#343638")
        self.style.configure("TLabel", foreground="#FFFFFF", background="#212121")
        self.style.configure("TLabelframe", foreground="#FFFFFF", background="#212121")
        self.style.configure("TEntry", foreground="#FFFFFF", background="#343638")
        self.style.configure("TProgressbar", foreground="#FFFFFF", background="#212121")

        self.root.configure(bg="#212121")  # Set the main background color

    def _create_widgets(self):
        # API Key entry frame
        self.api_key_frame = ttk.LabelFrame(self.root, text="API Key")
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(self.api_key_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_button = ttk.Button(self.api_key_frame, text="Set API Key", command=self._set_api_key)

        # File selection frame
        self.file_frame = ttk.LabelFrame(self.root, text="File Selection")
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, width=50)
        self.browse_button = ttk.Button(self.file_frame, text="Browse", command=self._browse_file)

        # Preview frame
        self.preview_frame = ttk.LabelFrame(self.root, text="Image Preview")
        self.preview_label = ttk.Label(self.preview_frame)

        # Progress frame
        self.progress_frame = ttk.LabelFrame(self.root, text="Progress")
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(self.progress_frame, textvariable=self.progress_var)
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')

        # Action buttons
        self.transcribe_button = ttk.Button(self.root, text="Transcribe", command=self._transcribe_image)
        self.transcribe_button.state(['disabled'])

    def _setup_layout(self):
        # API Key layout
        self.api_key_frame.pack(fill='x', padx=10, pady=5)
        self.api_key_entry.pack(side='left', padx=5, pady=5)
        self.api_key_button.pack(side='left', padx=5, pady=5)

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

    def _set_api_key(self):
        self.api_key = self.api_key_var.get()
        if self.api_key:
            try:
                self.api_client = GeminiAPIClient(api_key=self.api_key)
                messagebox.showinfo("API Key Set", "Gemini API key has been set.")
                self.transcribe_button.state(['!disabled'])
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "API Key cannot be empty")

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )

        if file_path:
            try:
                validate_image_file(file_path)
                self.file_path_var.set(file_path)
                self._update_preview(file_path)
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def _update_preview(self, file_path):
        image = Image.open(file_path)
        display_size = (300, 300)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        self.preview_label.configure(image=photo)
        self.preview_label.image = photo

    def _transcribe_image(self):
        if not self.api_client:
            messagebox.showerror("Error", "Please set the Gemini API key first.")
            return

        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an image file first")
            return

        self.progress_bar.start()
        self.progress_var.set("Processing image...")
        self.transcribe_button.state(['disabled'])

        try:
            processed_image = self.image_processor.prepare_image(file_path)
            transcription = self.api_client.transcribe_image(processed_image)

            try:
                date_str = extract_date(transcription)
                output_filename = f"{date_str}.txt"
            except ValueError:
                self.progress_var.set("No date found in transcription. Waiting for filename...")
                output_filename = self._prompt_for_filename()
                if not output_filename:
                    self.progress_var.set("Transcription completed but not saved (no filename provided)")
                    messagebox.showinfo("Transcription Complete",
                                        "Transcription completed but not saved as no filename was provided.")
                    return

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

    def _prompt_for_filename(self):
        filename = tk.simpledialog.askstring(
            "Filename Required",
            "No date found in the transcription.\nPlease enter a name for the output file:",
            parent=self.root
        )

        if filename:
            if not filename.lower().endswith('.txt'):
                filename += '.txt'
            return filename
        return None

    def mainloop(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = JournalTranscriberApp()
    app.mainloop()