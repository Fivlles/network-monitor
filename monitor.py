import os
import socket
import time
from datetime import datetime

import pg8000.dbapi
from dotenv import load_dotenv

load_dotenv()

# Κάθε πόσα δευτερόλεπτα γίνεται έλεγχος (από το .env, αλλιώς 60)
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "60"))


def log(text):
    """Τυπώνει μήνυμα με ημερομηνία και ώρα."""
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {text}", flush=True)


def get_connection():
    """Ανοίγει σύνδεση με τη βάση χρησιμοποιώντας τα στοιχεία από το .env."""
    return pg8000.dbapi.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def get_devices(conn):
    """Επιστρέφει όλες τις συσκευές από τον πίνακα devices."""
    cur = conn.cursor()
    cur.execute("SELECT id, name, ip_address, port FROM devices;")
    return cur.fetchall()


def check_device(host, port, timeout=3):
    """
    Προσπαθεί να συνδεθεί στο host:port.
    Επιστρέφει (True, latency_ms) αν πέτυχε, ή (False, None) αν απέτυχε.
    """
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency_ms = (time.perf_counter() - start) * 1000
            return True, round(latency_ms, 2)
    except OSError:
        return False, None


def save_check(conn, device_id, is_up, latency_ms):
    """Αποθηκεύει μία μέτρηση στον πίνακα checks."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO checks (device_id, is_up, latency_ms) VALUES (%s, %s, %s);",
        (device_id, is_up, latency_ms),
    )
    conn.commit()


def run_checks():
    """Ένας πλήρης γύρος: ελέγχει όλες τις συσκευές και αποθηκεύει τα αποτελέσματα."""
    conn = get_connection()
    try:
        for device_id, name, ip, port in get_devices(conn):
            is_up, latency = check_device(ip, port)
            save_check(conn, device_id, is_up, latency)
            status = "🟢 UP  " if is_up else "🔴 DOWN"
            log(f"{name:15} {ip:15} {status} {latency} ms")
    finally:
        conn.close()


def main():
    log(f"Το monitor ξεκίνησε. Έλεγχος κάθε {CHECK_INTERVAL} δευτερόλεπτα.")
    while True:
        try:
            run_checks()
        except Exception as e:
            log(f"⚠️ Σφάλμα στον γύρο ελέγχου: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Το monitor σταμάτησε.")