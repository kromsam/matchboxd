FROM python:3

# Set environment variables to avoid interaction during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required dependencies, including Firefox-ESR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    firefox-esr cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir virtualenv \
    && virtualenv venv \
    && . venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x cv_heart_lb.py
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]