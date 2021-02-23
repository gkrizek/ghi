# systemd

Below is an example of a systemd service file for Ghi. If you are running Ghi on your own server, this allows you to manage the Ghi process with systemd. This example will start Ghi with it listening on port `8080` and write its logs to systemd's journal logging system (accessible by `systemctl status ghi` for the last output and `journalctl -u ghi` for the log in full).

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
WorkingDirectory=/home/ubuntu/ghi
EnvironmentFile=/etc/default/ghi
ExecStart=/bin/bash -c "PYTHONPATH="/home/ubuntu/ghi/ghi:$PYTHONPATH" python3 /home/ubuntu/ghi/ghi/server.py --port 8080 --systemd
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

If you want you can redirect the log-output to the `/var/log/ghi.log` file by substituting `--systemd` with `&>> /var/log/ghi.log`.
_In that case you might need to create the log file first because the user might not have permissions to /var/log_

With this Service file, you can also set your environment variables in the `/etc/default/ghi` file and they will be automatically exported on start.