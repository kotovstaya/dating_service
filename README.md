1. cd deploy && docker build -f Dockerfile_simple -t dating_service_simple_image ./..
2. cd deploy && docker build -f Dockerfile_cuda -t dating_service_cuda_image ./..

Run telegram bot with webhook: 
1. ngrok http 8000
2. sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/dating_service-selfsigned.key -out /etc/ssl/certs/dating_service-selfsigned.crt -subj "/CN=\<ngrok dns\>"
3. /etc/nginx/sites-available/ create nginx.conf file
4. sudo ln -s /etc/nginx/sites-available/nginx /etc/nginx/sites-enabled/
5. docker compose -f docker-compose.dev.yaml up