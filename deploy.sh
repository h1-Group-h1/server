cd src
nohup uvicorn main:app --host 0.0.0.0 --ssl-keyfile=/etc/letsencrypt/live/com-ra-api.co.uk/privkey.pem --ssl-certfile=/etc/letsencrypt/live/com-ra-api.co.uk/fullchain.pem  --port 443
