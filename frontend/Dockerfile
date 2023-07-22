FROM node:13.12.0 as builder

WORKDIR /app

COPY package.json /app/package.json

RUN npm install

COPY . /app

RUN npm run build

FROM nginx:1.21.3-alpine

COPY --from=builder /app/build /usr/share/nginx/html

COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
