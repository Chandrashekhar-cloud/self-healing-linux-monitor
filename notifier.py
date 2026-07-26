import requests
import yaml
import os


def get_config_path():
    if os.path.exists("config.local.yaml"):
        return "config.local.yaml"
    return "config.yaml"


def load_webhook_url(config_path=None):
    if config_path is None:
        config_path = get_config_path()

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config.get("slack_webhook_url")


def send_alert(message, config_path=None):
    if config_path is None:
        config_path = get_config_path()

    webhook_url = load_webhook_url(config_path)

    if not webhook_url or "your/webhook" in webhook_url:
        print(f"[SLACK DISABLED] Would have sent: {message}")
        return

    payload = {
        "text": f":rotating_light: *Self-Healing Monitor Alert*\n{message}"
    }

    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except requests.RequestException as e:
        print(f"Failed to send Slack alert: {e}")
