FROM python:3.10-slim

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED TRUE

# install system dependencies
RUN apt-get update \
    && apt-get -y install git ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --no-cache-dir --upgrade pip

# set work directory
WORKDIR /app


# copy requirements.txt
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
COPY ./ /app/

# Start Flask API on port 8020 and send TCP message on port 8030
CMD ["gunicorn", "-b", "0.0.0.0:4100", "-t", "600","TTS:app"] 

