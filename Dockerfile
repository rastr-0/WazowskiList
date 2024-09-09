# basic docker image
FROM python:3.10-slim

# install git
RUN apt-get update && apt-get install -y git

# working directory
WORKDIR /docker_app

# copy requirements file
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy all the necessery directories to container
COPY app /docker_app/app
COPY tests /docker_app/tests

# Mark the mounted directory as a safe Git directory
RUN git config --global --add safe.directory /docker_app

# include working directory in python's path
ENV PYTHONPATH=/docker_app

# port app runs on
EXPOSE 8000

# run app in container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
