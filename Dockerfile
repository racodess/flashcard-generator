# Use official Python 3.12 image
FROM python:3.12

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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

# By default, run "python host.py" with a default folder
CMD ["python", "host.py", "./content"]
