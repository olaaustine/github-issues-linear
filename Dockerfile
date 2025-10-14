FROM python:3.11-slim

WORKDIR /app

# Install project dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY src ./src
COPY main.py ./

ENV PYTHONPATH=/app
# Default: run the app
CMD ["python", "main.py"]
