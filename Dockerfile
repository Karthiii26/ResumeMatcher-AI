# 1. Build frontend React assets
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 2. Package FastAPI backend and mount static assets
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy built static assets from frontend builder to 'static' folder
COPY --from=frontend-builder /app/frontend/dist ./static

# Copy python app source files
COPY api.py matcher.py parser.py explain.py ./
COPY sample_data ./sample_data

# Warm up the sentence-transformers cache by pre-downloading the model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Set unbuffered environment for uvicorn logs
ENV PYTHONUNBUFFERED=1

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Run uvicorn server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
