---
name: nginx-config-optimizer
description: >-
  Optimizes Nginx configurations for performance, security, caching, and load balancing with modern best practices. Use when users request "Nginx setup", "reverse proxy", "load balancer", "web server config", or "Nginx optimization".
license: MIT
metadata:
  version: "1.0"
  category: ci-cd-swe
---

# Nginx Config Optimizer

Create optimized Nginx configurations for high-performance web serving and reverse proxying.

## Core Workflow

1. **Define architecture**: Reverse proxy, load balancer, or static serving
2. **Configure security**: SSL/TLS, headers, rate limiting
3. **Optimize performance**: Caching, compression, buffers
4. **Setup upstream**: Backend server pools
5. **Add monitoring**: Access logs, metrics
6. **Test configuration**: Validate and reload

## Main Configuration

```nginx
# /etc/nginx/nginx.conf

user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;
pid /run/nginx.pid;

# Load dynamic modules
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 4096;
    multi_accept on;
    use epoll;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # Buffer settings
    client_body_buffer_size 16k;
    client_header_buffer_size 1k;
    client_max_body_size 50m;
    large_client_header_buffers 4 8k;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    log_format json escape=json '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"request":"$request",'
        '"status":$status,'
        '"body_bytes_sent":$body_bytes_sent,'
        '"request_time":$request_time,'
        '"upstream_response_time":"$upstream_response_time",'
        '"http_referer":"$http_referer",'
        '"http_user_agent":"$http_user_agent"'
    '}';

    access_log /var/log/nginx/access.log json;
    error_log /var/log/nginx/error.log warn;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy
        text/xml;

    # Brotli compression (if module available)
    # brotli on;
    # brotli_comp_level 6;
    # brotli_types text/plain text/css application/json application/javascript;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers (global)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    # Proxy cache
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=STATIC:10m inactive=7d use_temp_path=off max_size=1g;

    # Include site configs
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

## Best Practices

1. **Worker processes**: Set to `auto` for CPU cores
2. **Keepalive connections**: Enable for upstreams
3. **Gzip compression**: Enable for text content
4. **SSL/TLS**: Use TLS 1.2+ only
5. **Security headers**: Add HSTS, CSP, etc.
6. **Rate limiting**: Protect against abuse
7. **Buffer tuning**: Optimize for traffic patterns
8. **Caching**: Use proxy cache for static content

## Output Checklist

Every Nginx configuration should include:

- [ ] Worker process optimization
- [ ] Gzip compression enabled
- [ ] SSL/TLS with modern ciphers
- [ ] Security headers (HSTS, CSP, X-Frame-Options)
- [ ] Rate limiting zones
- [ ] Upstream keepalive connections
- [ ] Proper logging (JSON format)
- [ ] Health check endpoints
- [ ] Static file caching
- [ ] Proxy buffering tuned
- [ ] Error pages configured
- [ ] Configuration tested with `nginx -t`


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

