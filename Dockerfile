FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY streamlit_app ./streamlit_app
ENV STREAMLIT_SERVER_PORT=8080
EXPOSE 8080
CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
