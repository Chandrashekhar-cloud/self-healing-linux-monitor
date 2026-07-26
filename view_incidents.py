from incident_log import get_recent_incidents


def print_dashboard():
    incidents = get_recent_incidents(limit=15)
    print(f"{'TIMESTAMP':<26}{'TYPE':<14}{'VALUE':<10}{'ACTION'}")
    print("-" * 80)

    for ts, itype, val, action in incidents:
        print(f"{ts:<26}{itype:<14}{val:<10}{action}")


if __name__ == "__main__":
    print_dashboard()
