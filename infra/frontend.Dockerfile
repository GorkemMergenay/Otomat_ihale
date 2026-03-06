FROM node:20-alpine

WORKDIR /app/frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend .

RUN npm run build

CMD ["npm", "run", "start"]
