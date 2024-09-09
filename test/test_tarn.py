import time

from ratatosk_errands.model import TextToImageInstructions
from starlette.testclient import TestClient

from tarn.main import app


def test_gaze():
    with TestClient(app) as client:
        instructions = TextToImageInstructions(
            prompt="Ratatosk ascending Yggdrasil",
            image_identifier=str(time.time()),
            num_inference_steps=25,
            width=512,
            height=512
        )
        download_response = client.post("/gaze", json=instructions.model_dump())
        assert download_response.status_code == 200


def test_transmute():
    with TestClient(app) as client:
        with open("./yggdrasil.png", "rb") as file:
            response = client.post("/transmute",
                                   data={"prompt": "goats in a field", "strength": 0.5},
                                   files={"file": ("yggdrasil.png", file)})
            assert response.status_code == 200
