echo "Deploy script - will deploy application and mosquitto broker"
source /root/server/.venv/bin/activate
VER="1.3.1"
DEBUG_MODE=False VER=$VER python3 /root/server/src/main.py 
