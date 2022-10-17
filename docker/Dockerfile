FROM python

RUN apt update -y
RUN apt upgrade -y
RUN apt install python3-pip libpq-dev python3-dev -y && pip3 install --upgrade pip

ARG DEBIAN_FRONTEND=noninteractive
RUN apt install vim wget dpkg unzip tzdata -y
RUN wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_106.0.5249.119-1_amd64.deb
RUN apt install ./google-chrome-stable_106.0.5249.119-1_amd64.deb -y
RUN rm ./google-chrome-stable_106.0.5249.119-1_amd64.deb

RUN wget https://chromedriver.storage.googleapis.com/106.0.5249.61/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN rm chromedriver_linux64.zip

COPY app/ app/
COPY conf/ conf/
COPY .env .env
COPY requirements.txt requirements.txt
RUN pip3 install --no-deps -r requirements.txt

CMD ["python3", "app/app.py"]