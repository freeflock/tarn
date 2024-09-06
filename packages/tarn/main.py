import logging
import os
import time
import uuid

import requests
from fastapi import FastAPI
from ratatosk_errands.model import Errand, TextToImageInstructions, Echo

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

app = FastAPI()

GALLERY_HOST = os.getenv("GALLERY_HOST")
GALLERY_PORT = int(os.getenv("GALLERY_PORT"))
GALLERY_KEY = os.getenv("GALLERY_KEY")

STORAGE_DIRECTORY = os.getenv("STORAGE_DIRECTORY")
os.makedirs(STORAGE_DIRECTORY, exist_ok=True)


@app.post("/gaze")
def gaze(instructions: TextToImageInstructions):
    errand = Errand(
        instructions=instructions,
        origin="tarn:33333",
        destination="tarn:33333",
        errand_identifier=str(uuid.uuid4()),
        timestamp=time.time()
    )
    requests.post("http://errand_runner:33333/give_errand", json=errand.model_dump())


@app.post("/receive_echo")
def receive_echo(echo: Echo):
    headers = {"gallery_key": GALLERY_KEY}
    response = requests.post(f"http://{GALLERY_HOST}:{GALLERY_PORT}/download",
                             json={"file_name": f"{echo.reply.image_identifier}.png"},
                             headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"bad status code from gallery download: {response.status_code}")
    with open(f"{STORAGE_DIRECTORY}/{echo.reply.image_identifier}.png", "wb") as output_file:
        output_file.write(response.content)
