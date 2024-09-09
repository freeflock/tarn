import httpx
import requests
from ratatosk_errands.model import TextToImageInstructions


def test_gaze():
    instructions = TextToImageInstructions(
        prompt="An oil painting of Yggdrasil",
        image_identifier="yggdrasil"
    )
    response = requests.post("http://0.0.0.0:33322/gaze", json=instructions.model_dump())
    assert response.status_code == 200


def test_transmute():
    with open("./yggdrasil.png", "rb") as file:
        with httpx.Client(verify=False) as client:
            for i in range(10):
                response = client.post("http://0.0.0.0:33322/transmute",
                                       data={"prompt": "galaxy", "strength": i / 10},
                                       files={"file": (f"yggdrasil-{i}.png", file)})
            assert response.status_code == 200
