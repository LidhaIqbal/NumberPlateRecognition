"""
database.py - SQLite database management for Number Plate Recognition System
Handles vehicle records and scan history.
"""

import sqlite3
import os
from datetime import datetime

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vehicle_records.db")


def get_connection():
    """Return a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """
    Create tables and populate with fictional demo data if they don't exist.
    All records are clearly labelled as fictional demonstration data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Vehicle Records Table ──────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_no   TEXT    UNIQUE NOT NULL,
            owner_name        TEXT    NOT NULL,
            vehicle_type      TEXT    NOT NULL,
            vehicle_model     TEXT    NOT NULL,
            registration_status TEXT  NOT NULL DEFAULT 'Active',
            note              TEXT    DEFAULT '⚠️ Fictional demo record'
        )
    """)

    # ── Scan History Table ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            raw_ocr     TEXT,
            normalized  TEXT,
            matched     INTEGER NOT NULL DEFAULT 0,
            owner_name  TEXT,
            vehicle_type TEXT,
            vehicle_model TEXT
        )
    """)

    # ── Seed Demo Vehicles (only if table is empty) ─────────────────────────
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    count = cursor.fetchone()[0]
    if count == 0:
        demo_records = [
            ("MH12AB1234", "Rajesh Kumar (Demo)",    "Car",         "Maruti Swift",     "Active"),
            ("DL4CAF5678", "Priya Sharma (Demo)",    "Car",         "Honda City",        "Active"),
            ("KA03MN9012", "Arun Nair (Demo)",       "Motorcycle",  "Royal Enfield 350", "Active"),
            ("TN22XY3456", "Meena Patel (Demo)",     "Car",         "Toyota Innova",     "Expired"),
            ("GJ01BC7890", "Suresh Yadav (Demo)",    "Truck",       "Tata Ace",          "Active"),
            ("UP32EF2468", "Deepak Singh (Demo)",    "Car",         "Hyundai Creta",     "Active"),
            ("RJ14GH1357", "Kavita Joshi (Demo)",    "Car",         "Mahindra Scorpio",  "Suspended"),
            ("MH43WX8642", "Vikram Rao (Demo)",      "Van",         "Force Traveller",   "Active"),
        ]
        cursor.executemany("""
            INSERT INTO vehicles (registration_no, owner_name, vehicle_type, vehicle_model, registration_status)
            VALUES (?, ?, ?, ?, ?)
        """, demo_records)
        print(f"[DB] Seeded {len(demo_records)} fictional demo vehicle records.")

    conn.commit()
    conn.close()


# ── Vehicle Lookup ───────────────────────────────────────────────────────────

def normalize_plate(text: str) -> str:
    """Normalize a plate string: uppercase, strip spaces and special chars."""
    import re
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text.strip()


def lookup_vehicle(raw_text: str) -> dict | None:
    """
    Search the vehicle table for a registration matching the normalized OCR text.
    Returns a dict of vehicle details, or None if not found.
    """
    normalized = normalize_plate(raw_text)
    if not normalized:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT registration_no, owner_name, vehicle_type, vehicle_model, registration_status, note
        FROM vehicles
        WHERE UPPER(REPLACE(REPLACE(registration_no, ' ', ''), '-', '')) = ?
    """, (normalized,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "registration_no":      row[0],
            "owner_name":           row[1],
            "vehicle_type":         row[2],
            "vehicle_model":        row[3],
            "registration_status":  row[4],
            "note":                 row[5],
        }
    return None


def get_all_vehicles() -> list[dict]:
    """Return all vehicles in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, registration_no, owner_name, vehicle_type, vehicle_model, registration_status, note
        FROM vehicles ORDER BY id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "registration_no": r[1], "owner_name": r[2],
            "vehicle_type": r[3], "vehicle_model": r[4],
            "registration_status": r[5], "note": r[6]
        }
        for r in rows
    ]


# ── Scan History ─────────────────────────────────────────────────────────────

def save_scan(raw_ocr: str, normalized: str, matched: bool,
              owner_name: str = None, vehicle_type: str = None,
              vehicle_model: str = None):
    """Save a recognition attempt to the scan history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scan_history
            (timestamp, raw_ocr, normalized, matched, owner_name, vehicle_type, vehicle_model)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        raw_ocr, normalized, int(matched),
        owner_name, vehicle_type, vehicle_model
    ))
    conn.commit()
    conn.close()


def get_scan_history() -> list[dict]:
    """Return all scan history records, newest first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, raw_ocr, normalized, matched, owner_name, vehicle_type, vehicle_model
        FROM scan_history ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "timestamp": r[1], "raw_ocr": r[2],
            "normalized": r[3], "matched": bool(r[4]),
            "owner_name": r[5], "vehicle_type": r[6], "vehicle_model": r[7]
        }
        for r in rows
    ]


def clear_scan_history():
    """Delete all scan history records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scan_history")
    conn.commit()
    conn.close()


def get_summary_stats() -> dict:
    """Return summary statistics for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scan_history")
    total_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scan_history WHERE matched = 1")
    registered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scan_history WHERE matched = 0")
    unregistered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM vehicles")
    total_vehicles = cursor.fetchone()[0]

    conn.close()
    return {
        "total_scans":    total_scans,
        "registered":     registered,
        "unregistered":   unregistered,
        "total_vehicles": total_vehicles,
    }
