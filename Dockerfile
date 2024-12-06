# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default Chainlit port
EXPOSE 5000

# Command to run the Chainlit application
# CMD ["chainlit", "run", "app.py", "--host", "localhost", "--port", "5000"]  ##this can be done too
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "5000"]
