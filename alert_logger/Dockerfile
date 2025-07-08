FROM python:3.11-slim
WORKDIR /app
COPY alert_logger.py .
RUN pip install flask
EXPOSE 8080
CMD ["python", "alert_logger.py"] 