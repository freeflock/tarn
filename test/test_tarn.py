import time

import requests
from ratatosk_errands.model import TextToImageInstructions


def test_gaze():
    instructions = TextToImageInstructions(
        prompt="Ratatosk ascending Yggdrasil",
        image_identifier=str(time.time()),
        num_inference_steps=25,
        width=512,
        height=512
    )
    response = requests.post("http://0.0.0.0:33322/gaze", json=instructions.model_dump())
    assert response.status_code == 200
