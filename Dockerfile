FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update apt and install gcc
RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.10-slim

ENV DEBUG="False"
ENV DJANGO_LOG_LEVEL="INFO"
ENV ALLOWED_HOSTS="0.0.0.0"

ENV DATABASE_URL="sqlite:////app/db.sqlite3"

ENV CONTACT_EMAIL="cce23@ufaz.az"
ENV CONTACT_PHONE="+994 12 599 00 74"

ENV USE_S3="False"

ENV KB_ECOMM_CURRENCY="944"
ENV KB_ECOMM_LANGUAGE="EN"

WORKDIR /app

RUN addgroup --gid 1001 --system django && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group django


COPY --from=builder /app/wheels /wheels

RUN pip install --no-cache /wheels/*

COPY . /app

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 CMD curl --fail http://localhost:8000 || exit 1

RUN chown django:django /app -R

USER django

ENTRYPOINT ["./docker-entrypoint.sh"]