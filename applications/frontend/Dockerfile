FROM nginx:alpine

# Copy custom NGINX config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static assets into nginx html root
COPY src /usr/share/nginx/html

EXPOSE 80
