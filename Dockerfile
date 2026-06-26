# ---- Build Stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies if needed
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# ---- Runtime Stage ----
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# Copy application code
COPY main.py .
COPY app.py .

# Create output directory with correct permissions
RUN mkdir -p /app/output && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Streamlit runs on port 8501 by default
EXPOSE 8501

# Health check to ensure the app is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
