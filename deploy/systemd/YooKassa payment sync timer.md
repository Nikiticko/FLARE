# YooKassa payment sync timer

This timer runs pending YooKassa payment reconciliation every 5 minutes.

Install on the production server:

```bash
cp /var/www/shkila/deploy/systemd/shkila-payment-sync.service /etc/systemd/system/
cp /var/www/shkila/deploy/systemd/shkila-payment-sync.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now shkila-payment-sync.timer
```

Check status:

```bash
systemctl list-timers --all | grep shkila-payment-sync
systemctl status shkila-payment-sync.timer --no-pager
journalctl -u shkila-payment-sync.service -n 50 --no-pager
```

Run once manually:

```bash
systemctl start shkila-payment-sync.service
journalctl -u shkila-payment-sync.service -n 50 --no-pager
```

