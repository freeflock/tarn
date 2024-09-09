import os

from dotenv import load_dotenv

ENV_FILE_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/../env/test.env"
load_dotenv(ENV_FILE_PATH)
