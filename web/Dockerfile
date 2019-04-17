FROM nginx:latest

COPY ./certificate.crt /etc/ssl/certs/server.crt
COPY ./myKey.key /etc/ssl/private/server.key

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5000
