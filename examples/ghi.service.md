# systemd

Below is an example of a systemd service file for Ghi. If you are running Ghi on your own server, this allows you to manage the Ghi process with systemd. This example will start Ghi with it listening on port `8080` and write its logs to the `/var/log/ghi.log` file.

You can then start and stop it like so:

```
$ systemctl start ghi
$ systemctl stop ghi
```

**Location:**

`/var/lib/systemd/system/ghi.service`

**Content:**

```
[Unit]
Description=GitHub IRC Notification Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=python3 /opt/ghi/ghi/server.py --port 8080 &>> /var/log/ghi.log
Restart=on-failure
RestartSec=3
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
```