import os
from gui import JournalTranscriberApp

def main():
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key as an environment variable:")
        print("export GEMINI_API_KEY='your-api-key'")
        return

    # Start the application
    app = JournalTranscriberApp()
    app.mainloop()

if __name__ == "__main__":
    main()
