FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
COPY alembic/script.py.mako ./alembic/script.py.mako
RUN pip install --no-cache-dir .
ENV PYTHONPATH=/app/src
ENV OPERATOR_AUTH_REQUIRED=true
ENV SEED_ON_STARTUP=false
RUN mkdir -p /app/data
EXPOSE 8000
CMD sh -c "alembic upgrade head && if [ \"${SEED_ON_STARTUP:-false}\" = \"true\" ]; then python -m onboardpilot.services.seed; fi && uvicorn onboardpilot.main:app --host 0.0.0.0 --port ${PORT:-8000}"
