FROM python:3.10

WORKDIR /app

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.5.1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="$POETRY_HOME/bin:$PATH"

RUN pip install poetry==1.5.1
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY ./src/ ./

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "main.wsgi:application", "--bind", "0:8000"]
