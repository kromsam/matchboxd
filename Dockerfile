FROM python:3-alpine

# Update and install required dependencies, including Firefox and cron
RUN apk add --no-cache firefox
RUN apk add --no-cache cronie

WORKDIR /usr/src/app

COPY requirements.txt ./
# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x matchboxd_scraper
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]