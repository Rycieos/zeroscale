FROM python:3.9-alpine
MAINTAINER Mark Vander Stel <mvndrstl@gmail.com>

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir .[docker]

ENTRYPOINT ["docker-zeroscale"]
CMD ["--help"]
