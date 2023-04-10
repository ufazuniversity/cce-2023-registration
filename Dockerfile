FROM python:3.10-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update apt and install gcc
RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


FROM python:3.10-slim

WORKDIR /app

RUN addgroup --gid 1001 --system django && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group django


COPY --from=builder /app/wheels /wheels

RUN pip install --no-cache /wheels/*

COPY . /app

RUN python manage.py collectstatic --noinput &\
    python manage.py makemigrations &\
    python manage.py migrate

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 CMD curl --fail http://localhost:8000 || exit 1

RUN chown django:django /app -R

USER django

ENV DEBUG="False"
ENV DJANGO_LOG_LEVEL="INFO"
ENV ALLOWED_HOSTS="0.0.0.0"

ENV CONTACT_EMAIL="cce23@ufaz.az"
ENV CONTACT_PHONE="+994 12 599 00 74"

ENTRYPOINT ["gunicorn", "--workers", "4",\
            "--bind", "0.0.0.0:8000",\
            "--access-logfile", "-",\
            "--error-logfile", "-",\
            "--capture-output", "--log-level", "debug",\
            "--enable-stdio-inheritance",\
            "cce_2023_registration.wsgi:application"]