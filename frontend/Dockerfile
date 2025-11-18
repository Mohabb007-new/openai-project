# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package.json first to install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the code
COPY . .

EXPOSE 3010

CMD ["node", "app.js"]
