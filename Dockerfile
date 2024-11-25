FROM python:3.12-slim-bookworm AS base
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl git build-essential \
    && apt-get autoremove -y


FROM base AS install
WORKDIR /home/code

# cleanup
RUN apt-get purge -y curl git build-essential \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/*

FROM install as app-image

ENV PYTHONPATH=/home/code/ PYTHONHASHSEED=0

COPY ./requirements.txt /home/code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /home/code/requirements.txt

COPY app/ app/
COPY alembic/ alembic/
COPY .env alembic.ini ./

# create a non-root user and switch to it, for security.
RUN addgroup --system --gid 1001 "app-user"
RUN adduser --system --uid 1001 "app-user"
USER "app-user"