# Self-Healing Linux Monitor 

A lightweight Python tool that monitors system health (CPU, memory,
disk, inodes, critical services) and automatically remediates common
failures - restarting crashed services, terminating runaway processes,
and clearing disk space - while logging every incident to SQLite and
alerting via Slack.

## Features

- Threshold-based CPU / memory / disk / inode monitoring
- Automatic remediation: kill runaway processes, restart failed
  services, clear temp files
- Zombie process detection
- SQLite incident history
- Slack webhook alerting
- CLI dashboard to review past incidents

## Setup

pip install -r requirements.txt
python monitor.py

## Configuration

Edit config.yaml to set thresholds, services to watch, and your
Slack webhook URL.

## Why this project

Built to demonstrate the SRE troubleshooting loop end-to-end:
detect -> diagnose -> act -> log -> alert - rather than just
reporting metrics.
