# basic docker image
FROM python:3.10-slim

# working directory
WORKDIR /code

# copy requirements file
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy all the necessery directories to container
COPY app /code/app
COPY tests /tests

# port app runs on
EXPOSE 8000
# run app in container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
