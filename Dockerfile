FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    MODEL_PATH=/opt/models/all-MiniLM-L6-v2 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TORCH_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/models \
    && python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); model.save('/opt/models/all-MiniLM-L6-v2')"

ENV TRANSFORMERS_OFFLINE=1 \
    HF_HUB_OFFLINE=1

COPY api.py matcher.py model_runtime.py parser.py explain.py ./
COPY sample_data ./sample_data

EXPOSE 10000

CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-10000}
