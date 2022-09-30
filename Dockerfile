FROM python:3.8-slim
WORKDIR /usr/src/app

RUN apt update
RUN python -m venv venv
RUN . venv/bin/activate
RUN python -m pip install -U pip
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN apt-get update

COPY . .

EXPOSE 3333

CMD [ "python", "server.py" ]