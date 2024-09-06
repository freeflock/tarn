FROM python:3.11
WORKDIR /atelier

COPY ./requirements.txt /atelier/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /atelier/requirements.txt

COPY ./packages/tarn /atelier/tarn

CMD ["fastapi", "run", "tarn/main.py", "--port", "33333", "--workers", "1"]
