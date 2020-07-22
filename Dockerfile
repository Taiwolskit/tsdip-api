FROM python:slim
WORKDIR /usr/app
RUN apt-get update -y && \
    apt-get install -y gcc && \
    pip3 install pipenv==v2020.6.2
COPY Pipfile Pipfile.lock ./
RUN pipenv lock -r > requirements.txt && \
    pip3 install -r requirements.txt
COPY . .
CMD ["uwsgi", "--ini", "app.ini", "--py-autoreload", "1"]
