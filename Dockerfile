FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

COPY ./app /app/
COPY ["./.env", "/app/"]
ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--workers=3", "--host", "0.0.0.0", "--port", "8000"]