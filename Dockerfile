# Use official Python 3.12 image
FROM python:3.12

# Install required system packages
#   - poppler-utils (or poppler) for pdf2image
#   - weasyprint dependencies (libpango, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements to container
COPY ./setup/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into container
COPY . /app

# By default, run "python main.py" with a default folder
CMD ["python", "main.py", "test_input_dir"]
