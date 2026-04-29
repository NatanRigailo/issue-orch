FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS builder

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM base AS final

RUN useradd --no-create-home --shell /bin/false appuser

COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY main.py .

USER appuser

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
    CMD pgrep -f "python main.py" || exit 1

CMD ["python", "main.py"]
