
if [ $(which python3)  !=  $(pwd)/server-env/bin/python3 ]; then
  source ./server-env/bin/activate
fi

cd src
uvicorn main:app --host 0.0.0.0 --ssl-keyfile=/etc/letsencrypt/live/com-ra-api.co.uk/privkey.pem --ssl-certfile=/etc/letsencrypt/live/com-ra-api.co.uk/fullchain.pem  --port 443

