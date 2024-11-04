"""Entry point."""

import logging

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from .app import router
from .config import LOG_LEVEL, LOG_FORMAT
from .global_constants import DATABASE


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

# Create a FastAPI app
app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=DATABASE)

# Endpoint to handle the API request and database comparison
app.include_router(router, prefix="/api")
