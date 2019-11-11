FROM python:alpine
WORKDIR /usr/app
RUN apk add --no-cache --virtual .build-deps build-base musl-dev postgresql-dev && \
    apk add --no-cache --virtual .run-deps postgresql-libs && \
    pip3 install pipenv==v2018.11.26
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy && \
    apk del --no-cache .build-deps
COPY . .
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0" ]
