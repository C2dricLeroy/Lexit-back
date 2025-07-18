FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./entrypoint.sh /code/entrypoint.sh

RUN groupadd -r appuser || true && useradd -r -g appuser appuser || true

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*


RUN chmod +x /code/entrypoint.sh

COPY ./app /code/app

RUN groupadd -r appuser || true && useradd -r -g appuser appuser || true

RUN chown -R appuser:appuser /code

USER appuser

COPY ./app /code/app


CMD ["/code/entrypoint.sh"]