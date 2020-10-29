FROM python:slim
WORKDIR /usr/app
RUN apt-get update -y && \
    apt-get install -y gcc libpcre3 libpcre3-dev && \
    pip3 install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv lock -r > requirements.txt && \
    pip3 install -r requirements.txt
USER daemon
COPY . .
CMD ["uwsgi", "--ini", "app.ini"]
