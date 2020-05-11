FROM python:3.8-slim
MAINTAINER Mark Vander Stel <mvndrstl@gmail.com>

COPY . /app
WORKDIR /app

RUN pip install .[docker] && \
    rm -rf /root/.cache

ENTRYPOINT ["docker-zeroscale"]
CMD ["--help"]
