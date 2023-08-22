FROM node:13.12.0 as builder

WORKDIR /app

COPY package.json /app/package.json

RUN npm install

COPY . /app

RUN npm run build
