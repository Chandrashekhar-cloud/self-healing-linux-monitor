import psutil
import yaml
import time
import shutil
from remediate import (
    kill_top_cpu_process,
    kill_top_memory_process,
    clear_temp_files,
    restart_service,
)
from notifier import send_alert
from incident_log import log_incident


def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def check_cpu(threshold):
    usage = psutil.cpu_percent(interval=1)
    if usage > threshold:
        return True, usage
    return False, usage


def check_memory(threshold):
    mem = psutil.virtual_memory()
    if mem.percent > threshold:
        return True, mem.percent
    return False, mem.percent


def check_disk(threshold):
    disk = shutil.disk_usage("/")
    percent_used = (disk.used / disk.total) * 100
    if percent_used > threshold:
        return True, percent_used
    return False, percent_used


def check_inodes(threshold):
    # Uses statvfs for inode stats
    import os
    stats = os.statvfs("/")
    total_inodes = stats.f_files
    free_inodes = stats.f_ffree
    if total_inodes == 0:
        return False, 0
    used_percent = ((total_inodes - free_inodes) / total_inodes) * 100
    if used_percent > threshold:
        return True, used_percent
    return False, used_percent


def check_services(service_list):
    down_services = []
    for service in service_list:
        result = psutil.Process  # placeholder, real check below
    return down_services

def run_check_cycle(config):
    thresholds = config["thresholds"]

    cpu_breach, cpu_val = check_cpu(thresholds["cpu_percent"])
    if cpu_breach:
        print(f"[ALERT] High CPU usage: {cpu_val}%")
        action = kill_top_cpu_process()
        log_incident("cpu", cpu_val, action)
        send_alert(f"High CPU ({cpu_val}%) detected. Action taken: {action}")

    mem_breach, mem_val = check_memory(thresholds["memory_percent"])
    if mem_breach:
        print(f"[ALERT] High memory usage: {mem_val}%")
        action = kill_top_memory_process()
        log_incident("memory", mem_val, action)
        send_alert(f"High memory ({mem_val}%) detected. Action taken: {action}")

    disk_breach, disk_val = check_disk(thresholds["disk_percent"])
    if disk_breach:
        print(f"[ALERT] High disk usage: {disk_val:.1f}%")
        action = clear_temp_files()
        log_incident("disk", disk_val, action)
        send_alert(f"High disk usage ({disk_val:.1f}%). Action taken: {action}")

    inode_breach, inode_val = check_inodes(thresholds["inode_percent"])
    if inode_breach:
        print(f"[ALERT] High inode usage: {inode_val:.1f}%")
        log_incident("inode", inode_val, "manual review needed")
        send_alert(f"High inode usage ({inode_val:.1f}%). Manual review needed.")

    for service in config.get("services_to_watch", []):
        if not is_service_active(service):
            print(f"[ALERT] Service down: {service}")
            action = restart_service(service)
            log_incident("service_down", service, action)
            send_alert(f"Service {service} was down. Action taken: {action}")


def is_service_active(service_name):
    import subprocess
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True, text=True
    )
    return result.stdout.strip() == "active"


if __name__ == "__main__":
    config = load_config()
    interval = config.get("check_interval_seconds", 30)
    print("Self-Healing Monitor started. Watching system health...")

    while True:
        run_check_cycle(config)
        time.sleep(interval)
