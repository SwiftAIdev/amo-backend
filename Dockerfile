FROM python:3.10
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN apt-get update -y && apt-get upgrade -y  && apt-get install -y  make git zlib1g-dev libssl-dev gperf php-cli
COPY . /app
CMD ["python", "main.py"]


