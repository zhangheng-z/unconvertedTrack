FROM python:3.11-slim

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SQLITE_DATABASE_PATH=/shiqu_data/app.db \
    LOCAL_FILE_ROOT=/shiqu_data/files

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY web ./web

RUN python -m pip install --upgrade pip \
    && pip install -e . \
    && mkdir -p /shiqu_data/files /shiqu_data/logs

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
