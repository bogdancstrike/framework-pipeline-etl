# Use the official Node.js image as a base image
FROM node:16-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json into the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code into the container
COPY . .

# Build the React app for production
RUN npm run build

# Install a simple server to serve the build
RUN npm install -g serve

# Expose port 3000 for the frontend
EXPOSE 3000

# Command to serve the build
CMD ["serve", "-s", "build"]
