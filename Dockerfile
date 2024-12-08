FROM python:3-alpine

# Install Firefox and Cron
RUN apk add --no-cache firefox cronie

# Set working directory
WORKDIR /usr/src/app

# Install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy code and set permissions
COPY . .
RUN chmod +x matchboxd_scraper entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]