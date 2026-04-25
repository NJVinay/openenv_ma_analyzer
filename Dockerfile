# ── Base image ──
FROM python:3.11-slim

WORKDIR /app

# ── Install dependencies (layer caching) ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──
COPY . .

# ── Non-root user (HF Spaces requirement) ──
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# ── Expose HF Spaces port ──
EXPOSE 7860

# (Health check temporarily removed for Jupyter Lab)

# ── Run ──
RUN pip install jupyterlab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=7860", "--no-browser", "--allow-root", "--NotebookApp.token='hackathon'"]