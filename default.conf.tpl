{% if Addresses|length() %}
upstream {{ ID }} {
    ip_hash;
    {% for address in Addresses %}
        {% for port in Ports %}
            server {{ address }}:{{ port }};
        {% endfor %}
    {% endfor %}

}
{% endif %}

server {
    listen 80;
    server_name {{ ServerNames }};
    location / {
        {% if Addresses|length() %}
            proxy_pass http://{{ ID }};
        {% else %}
            {% for port in Ports %}
                proxy_pass http://$remote_addr:{{ port }};
            {% endfor %}
        {% endif %}
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}