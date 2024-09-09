import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import aiofiles
import httpx
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from ratatosk_errands.model import Errand, TextToImageInstructions, Echo, ImageToImageInstructions

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

GALLERY_HOST: str | None = None
GALLERY_PORT: int | None = None
GALLERY_KEY: str | None = None
STORAGE_DIRECTORY: str | None = None


def prepare_environment():
    global GALLERY_HOST
    GALLERY_HOST = os.getenv("GALLERY_HOST")
    assert GALLERY_HOST, "GALLERY_HOST env var not set"

    global GALLERY_PORT
    raw_gallery_port = os.getenv("GALLERY_PORT")
    assert raw_gallery_port, "GALLERY_PORT env var not set"
    GALLERY_PORT = int(raw_gallery_port)

    global GALLERY_KEY
    GALLERY_KEY = os.getenv("GALLERY_KEY")
    assert GALLERY_KEY, "GALLERY_KEY env var not set"

    global STORAGE_DIRECTORY
    STORAGE_DIRECTORY = os.getenv("STORAGE_DIRECTORY")
    assert STORAGE_DIRECTORY, "STORAGE_DIRECTORY env var not set"
    os.makedirs(STORAGE_DIRECTORY, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    prepare_environment()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/gaze")
async def gaze(instructions: TextToImageInstructions):
    async with httpx.AsyncClient(verify=False) as client:
        errand = Errand(
            instructions=instructions,
            origin="tarn",
            destination="tarn:33333/receive_echo",
            errand_identifier=str(uuid.uuid4()),
            timestamp=time.time()
        )
        ratatosk_response = await client.post("http://errand_runner:33333/give_errand", json=errand.model_dump())
        if ratatosk_response.status_code != 200:
            raise HTTPException(status_code=500, detail="failed to give errand to ratatosk")


@app.post("/transmute")
async def transmute(prompt: str = Form(...), strength: float = Form(...), file: UploadFile = File(...)):
    async with httpx.AsyncClient(verify=False) as client:
        base_image_identifier, file_extension = os.path.splitext(file.filename)
        gallery_response = await client.post(
            f"https://{GALLERY_HOST}:{GALLERY_PORT}/upload",
            files={"file": (file.filename, file.file)},
            headers={"gallery_key": GALLERY_KEY}
        )
        if gallery_response.status_code != 200:
            raise HTTPException(status_code=500, detail="failed to upload base image to gallery")
        errand = Errand(
            instructions=ImageToImageInstructions(
                prompt=prompt,
                image_identifier=f"{base_image_identifier}-transmuted",
                base_image_identifier=base_image_identifier,
                strength=strength
            ),
            origin="tarn",
            destination="tarn:33333/receive_echo",
            errand_identifier=str(uuid.uuid4()),
            timestamp=time.time()
        )
        ratatosk_response = await client.post("http://errand_runner:33333/give_errand", json=errand.model_dump())
        if ratatosk_response.status_code != 200:
            raise HTTPException(status_code=500, detail="failed to give errand to ratatosk")


@app.post("/receive_echo")
async def receive_echo(echo: Echo):
    async with httpx.AsyncClient(verify=False) as client:
        gallery_response = await client.post(f"https://{GALLERY_HOST}:{GALLERY_PORT}/download",
                                             json={"file_name": f"{echo.reply.image_identifier}.png"},
                                             headers={"gallery_key": GALLERY_KEY})
        if gallery_response.status_code != 200:
            raise HTTPException(status_code=500, detail="failed to download image from gallery")
        async with aiofiles.open(f"{STORAGE_DIRECTORY}/{echo.reply.image_identifier}.png", mode="wb") as output_file:
            await output_file.write(gallery_response.content)
