FROM python:3.11
WORKDIR /app
COPY ./app/lect_task.py /app
RUN pip install Flask
EXPOSE 5000
CMD ["python", "lect_task.py"]
