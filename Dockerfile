FROM python:3.11.9
WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt

COPY __init__.py /app/__init__.py
COPY main.py /app/main.py
COPY Makefile /app/Makefile
COPY /data /app/data
COPY /src /app/src
COPY /easyocr /app/easyocr
COPY /yolo /app/yolo

EXPOSE 8000
ENTRYPOINT ["uvicorn", "main:app", "--proxy-headers", "--forwarded-allow-ips=*", "--host", "0.0.0.0", "--port", "8000"]