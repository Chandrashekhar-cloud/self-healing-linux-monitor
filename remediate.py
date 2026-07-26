import psutil
import subprocess
import os
import glob


def kill_top_cpu_process(exclude_pids=None):
    """Find and kill the process consuming the most CPU (excluding critical PIDs)."""
    exclude_pids = exclude_pids or [1]  # never kill init/systemd
    procs = [(p.pid, p.info["cpu_percent"], p.info["name"])
             for p in psutil.process_iter(["cpu_percent", "name"])
             if p.pid not in exclude_pids]
    if not procs:
        return "no candidate process found"
    procs.sort(key=lambda x: x[1], reverse=True)
    top_pid, cpu_val, name = procs[0]
    try:
        psutil.Process(top_pid).terminate()
        return f"terminated PID {top_pid} ({name}), was using {cpu_val}% CPU"
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return f"failed to terminate PID {top_pid}: {e}"


def kill_top_memory_process(exclude_pids=None):
    """Find and kill the process consuming the most memory."""
    exclude_pids = exclude_pids or [1]
    procs = [(p.pid, p.info["memory_percent"], p.info["name"])
             for p in psutil.process_iter(["memory_percent", "name"])
             if p.pid not in exclude_pids]
    if not procs:
        return "no candidate process found"
    procs.sort(key=lambda x: x[1], reverse=True)
    top_pid, mem_val, name = procs[0]
    try:
        psutil.Process(top_pid).terminate()
        return f"terminated PID {top_pid} ({name}), was using {mem_val:.1f}% memory"
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return f"failed to terminate PID {top_pid}: {e}"


def clear_temp_files(paths=None):
    """Clear common temp/cache locations to free disk space."""
    paths = paths or ["/tmp/*", "/var/tmp/*"]
    freed_files = 0
    for pattern in paths:
        for filepath in glob.glob(pattern):
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    freed_files += 1
            except (PermissionError, FileNotFoundError):
                continue
    return f"removed {freed_files} temp files"


def restart_service(service_name):
    """Restart a systemd service."""
    try:
        result = subprocess.run(
            ["systemctl", "restart", service_name],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return f"restarted {service_name} successfully"
        return f"failed to restart {service_name}: {result.stderr.strip()}"
    except Exception as e:
        return f"error restarting {service_name}: {e}"


def find_zombie_processes():
    """Detect zombie processes for logging (cannot be killed directly — parent must reap)."""
    zombies = []
    for p in psutil.process_iter(["pid", "name", "status"]):
        if p.info["status"] == psutil.STATUS_ZOMBIE:
            zombies.append((p.info["pid"], p.info["name"]))
    return zombies
