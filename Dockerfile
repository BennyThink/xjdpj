FROM python:3.12-alpine AS pybuilder
RUN pip install -U pdm && pdm config python.use_venv false
ADD backend/pyproject.toml backend/pdm.lock /build/
WORKDIR /build
RUN pdm install --prod

FROM node:20-alpine AS nodebuilder
WORKDIR /build
ADD frontend /build
RUN npm install && npm run build



FROM python:3.12-alpine
WORKDIR /app
COPY --from=pybuilder /build/__pypackages__/3.12/bin /usr/local/bin/
COPY --from=pybuilder /build/__pypackages__/3.12/lib /usr/local/lib/python3.12/

COPY --from=nodebuilder /build/dist /frontend/dist
COPY backend /app
WORKDIR /app

CMD [ "sanic", "main:app", "--host=0.0.0.0", "--port=44777", "--access-logs", "--fast" ]