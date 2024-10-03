FROM alpine:latest

# Install Nginx and headers-more module
RUN apk add --no-cache nginx nginx-mod-http-headers-more

# Copy main Nginx configuration (if you don't have this, add it)
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports 80 and 443
EXPOSE 80 443

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
