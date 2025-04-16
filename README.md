# Moviepy-API

## Overview

This project provides a Python API and command-line tool for generating short videos from text. It leverages the MoviePy library for video editing and `edge-tts` for text-to-speech conversion using Microsoft Edge voices. The API is built using FastAPI, allowing for easy integration into web applications.

## Use Cases

- **Automated Content Creation:** Generate engaging short videos for platforms like YouTube Shorts and TikTok from textual content.
- **Social Media Marketing:** Quickly create video snippets for social media campaigns.
- **Educational Content:**  Transform articles or scripts into video format for wider accessibility.
- **Personalized Video Messages:**  Create custom video messages with text-to-speech narration.

## Features

- **Text-to-Speech:** Uses `edge-tts` to generate natural-sounding voiceovers in various languages and voices.
- **Background Video:** Randomly selects and loops background video clips from the `Video/` folder to create visually engaging content.
- **Background Music:** Adds background music from the `Audio/` folder to enhance the video's atmosphere.
- **Subtitles:** Automatically generates and adds subtitles to the video based on the text content.
- **Platform-Specific Output:** Supports output formats optimized for YouTube Shorts and TikTok.
- **API and CLI Interface:**  Offers both a REST API for programmatic video generation and a command-line interface for quick use.
- **Video Segmentation for Youtube:** Automatically splits longer videos into segments suitable for YouTube Shorts.

## Libraries Used

- **fastapi:**  For building the REST API.
- **uvicorn:** ASGI server to run the FastAPI application.
- **moviepy:** For video editing and manipulation.
- **edge-tts:** For text-to-speech conversion using Microsoft Edge voices.
- **pydantic:** For data validation and settings management in FastAPI.
- **python-multipart:** For handling file uploads in FastAPI.
- **aiofiles:** For asynchronous file operations in FastAPI.

## How to Use

### Prerequisites

- **Python 3.7+**
- **FFmpeg:** Make sure FFmpeg is installed on your system and accessible in your system's PATH environment variable. MoviePy relies on FFmpeg for video processing.
- **Internet Connection:** `edge-tts` requires an internet connection to access Microsoft Edge's text-to-speech service.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [repository_url]
   cd Moviepy-API
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Command-Line Interface (CLI)

1. **Prepare your input text:** Create a text file (e.g., `input.txt`) with the text you want to convert to video.

2. **Run `main.py`:**
   ```bash
   python main.py input.txt
   ```
   - This command will generate YouTube Shorts and save them in the `Outputs/Youtube/` directory as a zip file (`Youtube_Shorts.zip`).
   - The TikTok video will be saved as `Outputs/Tiktok/TikTok.mp4`.
   - You can modify the default voice, rate, words in cue, subclip length, and platform in the `if __name__ == "__main__":` block of `main.py`.

### API Usage

1. **Run the FastAPI application:**
   ```bash
   python mainAPI.py
   ```
   - This starts the API server at `http://127.0.0.1:8000`.

2. **API Endpoints:**

   - **GET `/`**:  Returns default parameters for video generation. Useful for understanding the input format.
     - Example: `http://127.0.0.1:8000/`

   - **POST `/generate`**:  Generates a video based on the provided JSON input.
     - Request Body (JSON):
       ```json
       {
           "text": "Your text here",
           "voice": "en-US-BrianMultilingualNeural",
           "rate": "+7%",
           "words_in_cue": 1,
           "subclip_length": 15,
           "platform": "youtube"  // or "tiktok"
       }
       ```
     - Response:
       ```json
       {
           "status": "Accepted",
           "task_id": "unique_task_id"
       }
       ```
     - Status Codes:
       - `202 Accepted`:  Video generation task accepted and running in the background.
       - `422 Unprocessable Entity`: Input validation error.

   - **GET `/status/{task_id}`**:  Checks the status of a video generation task.
     - Example: `http://127.0.0.1:8000/status/your_task_id`
     - Response:
       ```json
       {
           "task_id": "your_task_id",
           "status": "Pending" | "In Progress" | "Completed" | "Failed: error_message"
       }
       ```
     - Status Codes:
       - `200 OK`: Task status retrieved successfully.
       - `404 Not Found`: Task ID not found.

   - **GET `/download/{task_id}`**:  Downloads the generated video file once the task is completed.
     - Example: `http://127.0.0.1:8000/download/your_task_id`
     - Response:  Video file as an attachment.
     - Status Codes:
       - `200 OK`: Video file download.
       - `404 Not Found`: Task ID or file not found.

### Project Structure

```
Moviepy-API-main/
├── Audio/                     # Folder for background audio files (MP3, M4A, WAV)
│   ├── broken sonata sad piano.mp3
│   ├── ...                   # More audio files
├── Font/                      # Folder for fonts (TTF)
│   └── PassionOne-Bold.ttf
├── Outputs/                   # Folder for output videos
│   ├── Tiktok/                # TikTok output videos
│   │   └── TikTok.mp4
│   └── Youtube/               # YouTube Shorts output videos
│       ├── Youtube_Short.mp4
│       ├── Youtube_Shorts.zip
│       └── Part_1.mp4         # Segmented video parts for YouTube
├── Video/                     # Folder for background video clips (MP4, AVI, MOV, MKV)
│   ├── Test_Clip_1.mp4
│   ├── ...                   # More video clips
├── Voice/                     # Folder for voice-related output
│   ├── Audio.mp3              # Generated voice audio file
│   └── Audio.srt              # Subtitle file (SRT format)
├── LICENSE                    # Project license (GNU GPL v3)
├── main.py                    # Main script for video generation (CLI)
├── mainAPI.py                 # FastAPI application for API access
├── README.md                  # Project documentation (this file)
├── requirements.txt           # Project dependencies
└── test.txt                   # Example input text file

```

### Customization

- **Background Videos:** Add your own video clips to the `Video/` folder. Ensure they are in `.mp4`, `.avi`, `.mov`, or `.mkv` format.
- **Background Music:**  Place your audio files (`.mp3`, `.m4a`, `.wav`) in the `Audio/` folder.
- **Voice Settings:**  Modify voice parameters (voice, rate, words_in_cue) in `main.py` or when calling the API to customize the text-to-speech output.
- **Font:** Change the font used for subtitles by replacing `Font/PassionOne-Bold.ttf` and updating the `font_path` variable in `main.py`.
- **Output Paths:**  Adjust output paths in `main.py` if needed.
- **Video Editing Parameters:**  Customize video editing parameters like subclip length, segment duration, and overlap in `main.py`.

### License

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.

---

**Note:** This README provides a comprehensive overview of the project. For detailed code-level documentation, please refer to the comments within the Python scripts (`main.py` and `mainAPI.py`).
