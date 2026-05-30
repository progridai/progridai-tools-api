FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (build-essential needed for some python packages if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy Portuguese model required by Presidio
RUN python -m spacy download pt_core_news_lg

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
