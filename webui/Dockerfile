FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create requirements.txt on the fly
RUN echo "streamlit\npandas\nsqlalchemy\npsycopg2-binary\npycountry" > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source
COPY app.py .

EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]