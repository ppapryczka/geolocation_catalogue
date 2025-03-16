#!/bin/bash

alembic upgrade head
uvicorn geolocation_catalogue.main:app --port 8000 --host 0.0.0.0
