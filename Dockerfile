FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./entrypoint.sh /code/entrypoint.sh

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN chmod +x /code/entrypoint.sh

COPY ./app /code/app

RUN chown -R appuser:appuser /code

USER appuser

COPY ./app /code/app


CMD ["/code/entrypoint.sh"]