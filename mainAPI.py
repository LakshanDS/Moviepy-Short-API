import os
import uuid
import asyncio
from typing import Literal, Dict
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from main import editor

app = FastAPI()

# In-memory storage for task status and file paths
task_status: Dict[str, str] = {}
task_file_paths: Dict[str, str] = {}

class TextInput(BaseModel):
    text: str = "I Will make your text speak!"
    voice: str = "en-US-BrianMultilingualNeural"
    rate: str = "+7%"
    words_in_cue: int = 1
    subclip_length: int = 15
    platform: Literal["youtube", "tiktok"] = "youtube"

async def process_video(task_id: str, text: str, voice: str, rate: str, words_in_cue: int, subclip_length: int, platform: str):
    try:
        # Update task status to "In Progress"
        task_status[task_id] = "In Progress"
        file_path = await editor(text, voice, rate, words_in_cue, subclip_length, platform)
        # Update task status to "Completed" with the file path
        task_status[task_id] = "Completed"
        task_file_paths[task_id] = file_path
    except Exception as e:
        # Update task status to "Failed"
        task_status[task_id] = f"Failed: {str(e)}"

@app.get("/")
async def root():
    return {"text": "I Will make your text speak!", "voice": "en-US-BrianMultilingualNeural", "rate": "+7%", "words_in_cue": 1, "subclip_length": 15, "platform": "youtube"}

@app.post("/generate")
async def generate(input: TextInput, background_tasks: BackgroundTasks):
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    task_status[task_id] = "Accepted"

    background_tasks.add_task(process_video, task_id, input.text, input.voice, input.rate, input.words_in_cue, input.subclip_length, input.platform)
    return JSONResponse(content={"status": "Accepted", "task_id": task_id}, status_code=202)

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    status = task_status.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={"task_id": task_id, "status": status})
    print(status)

@app.get("/download/{task_id}")
def download(task_id: str):
    file_path = task_file_paths.get(task_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type='application/octet-stream', filename=os.path.basename(file_path))
    print("download Successful!")

# Ensure main only runs if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# ssl_keyfile="/etc/letsencrypt/live/lakminecraft.duckdns.org/privkey.pem"
# ssl_certfile="/etc/letsencrypt/live/lakminecraft.duckdns.org/fullchain.pem"