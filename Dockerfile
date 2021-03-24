FROM python:3.9

RUN python -m pip install --upgrade pip \
    && pip install poetry
ADD pyproject.toml poetry.lock ./

ARG extras=server
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --extras "$extras"

ADD blog_app ./blog_app
ADD tests ./tests
ADD cli ./cli

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "blog_app:app"]
