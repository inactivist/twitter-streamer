FROM python:3.8-slim-buster
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER 1000
ENTRYPOINT [ "python", "-m", "streamer.streamer"]