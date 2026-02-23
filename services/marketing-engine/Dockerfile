FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    useradd -m -u 1000 appuser && chown -R appuser:appuser /app

COPY app.py ./

USER appuser

EXPOSE 8101

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:8101/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8101"]
