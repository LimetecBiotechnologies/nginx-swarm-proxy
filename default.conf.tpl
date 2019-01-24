server {
    listen 80;
    server_name {{ container.ServerNames }};
    location / {
        proxy_pass http://$remote_addr:{{ container.ServerPort }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}