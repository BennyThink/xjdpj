FROM python:3.14-alpine AS pybuilder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ADD backend/pyproject.toml backend/uv.lock /app/
WORKDIR /app
RUN uv sync --frozen --no-dev

FROM node:24-alpine AS nodebuilder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json /app/
RUN npm ci
COPY frontend /app
RUN npm run build


FROM python:3.14-alpine
WORKDIR /app
COPY --from=pybuilder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=nodebuilder /app/dist /frontend/dist
COPY backend /app
WORKDIR /app

CMD [ "sanic", "main:app", "--host=0.0.0.0", "--port=44777", "--access-logs", "--fast" ]