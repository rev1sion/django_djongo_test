FROM python:3.6-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	TZ=Europe/Kiev \
	LANG=C.UTF-8 \
	APP_DIR=/app \
	DEBIAN_FRONTEND=noninteractive

ARG GID=1000
ARG UID=1000
ARG USER=ubuntu

RUN groupadd $USER && useradd -ms /home/$USER -g root -G sudo,$USER -u 1001 $USER
WORKDIR $APP_DIR
RUN apt-get update  \
    && apt-get install --assume-yes --no-install-recommends gcc libssl-dev libxml2-dev htop libxslt1-dev build-essential \
    default-libmysqlclient-dev python3-pip python3-dev \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/* && rm -rf /tmp/* /var/tmp/*

COPY --chown=$USER:$USER ./django_proj $APP_DIR

RUN pip install --upgrade pip && pip install -r $APP_DIR/requirements.txt

COPY ./docker/dev/django_app/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

#ENTRYPOINT ["tail", "-f", "/dev/null"]
