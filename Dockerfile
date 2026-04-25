# ── Base image ──
FROM pytorch/pytorch:2.1.2-cuda11.8-cudnn8-devel

# Install git for unsloth
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

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

# ── Run ──
ENV PATH="/home/appuser/.local/bin:${PATH}"
RUN pip install jupyterlab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=7860", "--no-browser", "--allow-root", "--NotebookApp.token='hackathon'"]