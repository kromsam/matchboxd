FROM python:3-alpine

# Update and install required dependencies, including Firefox-ESR
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    cron && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x matchboxd_scraper
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]