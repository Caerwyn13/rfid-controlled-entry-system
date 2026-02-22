"""
TCP server that receives access events from the ESP32 and logs them.

The ESP32 sends a single CSV line per scan:
    <UID>,<GRANTED>,<MILLIS>\n

    UID     - hex string, e.g. "BD 31 15 2B"
    GRANTED - 1 (access granted) or 0 (access denied)
    MILLIS  - milliseconds since the ESP32 last booted
"""

import csv
import socket
import os
from datetime import datetime, timezone


# ── Configuration ────────────────────────────────────────────
HOST        = "192.168.1.50"
PORT        = 5000
BUFFER_SIZE = 1024
LOG_FILE    = "access_log.csv"


# ── CSV log setup ────────────────────────────────────────────
CSV_HEADERS = ["timestamp_utc", "uid", "granted", "device_millis", "client_ip"]

def initialise_log():
    """Create the CSV log file with headers if it does not already exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADERS)


def log_event(uid: str, granted: bool, device_millis: str, client_ip: str):
    """Append one access event to the CSV log."""
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow([timestamp, uid, int(granted), device_millis, client_ip])


# ── Packet parsing ───────────────────────────────────────────
def parse_payload(raw: str) -> tuple[str, bool, str] | None:
    """
    Parse a CSV line sent by the ESP32.
    Expected format: <UID>,<GRANTED>,<MILLIS>
    Returns (uid, granted, millis) or None if malformed.
    """
    parts = raw.strip().split(",")
    if len(parts) != 3:
        return None

    uid, granted_str, millis = parts[0].strip(), parts[1].strip(), parts[2].strip()

    if granted_str not in ("0", "1"):
        return None

    return uid, granted_str == "1", millis


# ── Main server loop ─────────────────────────────────────────
def run_server():
    initialise_log()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"[SERVER] Listening on {HOST}:{PORT}")
    print(f"[SERVER] Logging to '{LOG_FILE}'")
    print("[SERVER] Press Ctrl+C to stop.\n")

    try:
        while True:
            client_socket, address = server_socket.accept()
            client_ip = address[0]
            print(f"[CONNECT] Connection from {client_ip}")

            try:
                raw_data = client_socket.recv(BUFFER_SIZE).decode("utf-8")
            except UnicodeDecodeError:
                print(f"[WARN] Non-UTF-8 data from {client_ip} — ignoring")
                client_socket.close()
                continue

            if not raw_data:
                print(f"[WARN] Empty payload from {client_ip}")
                client_socket.close()
                continue

            print(f"[RECV] {raw_data.strip()!r}")

            parsed = parse_payload(raw_data)
            if parsed is None:
                print(f"[WARN] Malformed payload from {client_ip}: {raw_data.strip()!r}")
                client_socket.close()
                continue

            uid, granted, millis = parsed
            print(f"[EVENT] UID={uid!r}  Status={'GRANTED' if granted else 'DENIED'}  Uptime={millis}ms")

            log_event(uid, granted, millis, client_ip)
            print(f"[LOG]   Written to {LOG_FILE}\n")

            client_socket.close()

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down gracefully...")
    finally:
        server_socket.close()
        print("[SERVER] Socket closed.")


if __name__ == "__main__":
    run_server()
