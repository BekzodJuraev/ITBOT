# Step 1: Use an official Python image as a parent image
FROM python:3.9-slim

# Step 2: Set environment variables to prevent Python from writing .pyc files and buffering output
ENV PYTHONUNBUFFERED 1

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Copy the requirements.txt into the container
COPY requirements.txt /app/

# Step 5: Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the Django project (ITBOT folder and other files) into the container
COPY . /app/

# Step 7: Expose port 8000 for Django (change this port if needed)
EXPOSE 8000

# Step 8: Run the Django development server (you can change this for production)
CMD python manage.py runserver 0.0.0.0:8000

