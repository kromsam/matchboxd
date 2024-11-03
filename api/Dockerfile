FROM python:latest

WORKDIR /usr/src/app/api

COPY ./requirements.txt ./
# Install virtualenv and create a virtual environment
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD [CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]]