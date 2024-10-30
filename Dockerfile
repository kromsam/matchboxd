FROM python:3-alpine

# Update and install required dependencies, including Firefox-ESR
RUN apk add --no-cache firefox
RUN apk add --no-cache cronie

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