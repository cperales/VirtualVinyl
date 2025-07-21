FROM python:3.13-slim
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY streamlit_app ./streamlit_app

# Copy environment variables (make sure to create this file)
# COPY .env ./
ENV SPOTIPY_CLIENT_ID=YOUR_CLIENT_ID
ENV SPOTIPY_CLIENT_SECRET=YOUR_CLIENT_SECRET
ENV REDIRECT_URI=URL

# Set Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8080

CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.headless", "true"]
