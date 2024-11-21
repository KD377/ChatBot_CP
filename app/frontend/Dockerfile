# Use the official Node.js image
FROM node:16

# Set working directory
WORKDIR /app/frontend

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy frontend code
COPY . .

# Expose the port for React
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
