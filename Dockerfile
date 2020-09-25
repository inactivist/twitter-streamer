FROM python:2.7.18-slim-buster

WORKDIR ./

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "./streamer/streamer.py" ]