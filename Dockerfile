FROM python:3.11.0-bullseye

ARG ASSETS_FOLDER="example/assets/"
ARG PORT=8084

WORKDIR /app

# assets
RUN mkdir "assets"
COPY $ASSETS_FOLDER/* assets

# source code
RUN mkdir "scripts"
COPY scripts/* scripts

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PORT_ENV=${PORT}

# start server on container start
CMD python scripts/server.py --assets_folder "assets" --port ${PORT_ENV} --host "0.0.0.0"
