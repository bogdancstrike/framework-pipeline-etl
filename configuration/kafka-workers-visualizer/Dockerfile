# Step 1: Build the React app
FROM node:16-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY ./ ./
RUN npm run build

# Step 2: Serve the React app with Nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 to serve the app
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# docker build --no-cache -t kafka-workers-visualizer:latest .
# docker tag kafka-workers-visualizer:latest localhost:32000/kafka-workers-visualizer:latest
# docker push localhost:32000/kafka-workers-visualizer:latest