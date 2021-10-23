cp ra-server.service /etc/systemd/system/
systemctl daemon-reload
systemctl start mosquitto.service
systemctl start ra-server.service
