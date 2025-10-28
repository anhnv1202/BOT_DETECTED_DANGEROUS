# ===== Builder =====
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build deps (chỉ dùng để build wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

# Tạo venv để đóng gói dependencies
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && \
    python -m pip install --upgrade pip setuptools wheel && \
    # Cài torch CPU wheel để giảm size
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
    # pip install --no-cache-dir -r requirements.txt
# ===== Runtime =====
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Runtime libs tối thiểu cho Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-turbo-progs \
    libjpeg62-turbo \
    zlib1g \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv đã cài deps (không mang build-essential)
COPY --from=builder /opt/venv /opt/venv

# Copy code tối thiểu để chạy
COPY app ./app
COPY mobilenetv2_dangerous_objects.pth ./

VOLUME ["/app/data"]

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]