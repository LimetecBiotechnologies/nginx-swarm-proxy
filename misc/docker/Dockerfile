FROM nginx:alpine

RUN mkdir -p /app && \
    apk add python3 && \
    pip3 install docker && \
    pip3 install Jinja2

EXPOSE 80

STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]