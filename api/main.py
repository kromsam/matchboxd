"""Entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware

from api.app import router
from api.global_constants import LOG_LEVEL, LOG_FORMAT, DATABASE
from api.db_helpers import DatabaseHandler

# Set up logging

# Map the string representation to the corresponding logging level constant
numeric_log_level = getattr(logging, LOG_LEVEL, None)

logging.basicConfig(
    level=numeric_log_level,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        # Add other handlers if needed
    ],
)

# Initialize the database
db_handler = DatabaseHandler(DATABASE)
db_handler.create_all()

# Create a FastAPI app
app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=DATABASE)

# Configure CORS
origins = [
    "http://localhost:5371",  # Frontend URL
    "http://matchboxd_web:5371",  # Docker frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to handle the API request and database comparison
app.include_router(router, prefix="/api")
