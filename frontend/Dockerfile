FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build for production
RUN npm run build

# Expose port
EXPOSE 5173

# Run dev server
CMD ["npm", "run", "dev"]
