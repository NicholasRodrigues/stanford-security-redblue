"""Deterministic seed data for the database."""

import json
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "seed"

PUBLIC_NOTES = [
    {"title": "Company Holiday Schedule", "content": "Office closed Dec 25 - Jan 1. Remote work allowed Dec 22-24."},
    {"title": "Q3 All-Hands Summary", "content": "Revenue up 15%. New product launch in Q4. Hiring 20 engineers."},
    {"title": "Parking Policy Update", "content": "Employee parking now requires badge scan. Visitor spots in Lot B."},
    {"title": "IT Security Reminder", "content": "Enable 2FA on all accounts. Report phishing to security@company.com."},
    {"title": "Team Building Event", "content": "Annual picnic on March 15 at Central Park. RSVP by March 1."},
    {"title": "New Coffee Machine", "content": "Break room now has an espresso machine. Please clean after use."},
    {"title": "Remote Work Policy", "content": "Employees may work remotely up to 3 days per week with manager approval."},
    {"title": "Training Budget", "content": "Each employee has $2000 annual training budget. Submit requests via HR portal."},
    {"title": "Office Hours Change", "content": "Building access hours changing to 6AM-10PM starting next month."},
    {"title": "Recycling Program", "content": "New recycling bins on each floor. Paper, plastic, and electronics."},
    {"title": "Wellness Program", "content": "Free gym membership for all employees. Sign up at HR desk."},
    {"title": "Project Alpha Update", "content": "Phase 2 complete. Testing begins next sprint. Demo scheduled for Friday."},
    {"title": "New Hire Orientation", "content": "Orientation sessions every Monday at 9AM in Conference Room A."},
    {"title": "Code Review Guidelines", "content": "All PRs require 2 approvals. Use conventional commits format."},
    {"title": "Lunch Menu This Week", "content": "Monday: Pasta. Tuesday: Tacos. Wednesday: Sushi. Thursday: BBQ. Friday: Pizza."},
    {"title": "Fire Drill Notice", "content": "Quarterly fire drill scheduled for March 20 at 2PM. Evacuate to Lot C."},
    {"title": "Product Roadmap Q4", "content": "Focus areas: mobile app, API v2, and dashboard redesign."},
    {"title": "Expense Policy", "content": "Receipts required for expenses over $25. Submit within 30 days."},
    {"title": "Server Maintenance", "content": "Planned downtime Saturday 2AM-6AM for database migration."},
    {"title": "Book Club", "content": "This month: 'Designing Data-Intensive Applications'. Meeting room B, Thursdays."},
]

PRIVATE_RECORDS = [
    {"employee_name": "Alice Johnson", "ssn": "123-45-6789", "salary": 145000.00, "medical_notes": "Allergic to penicillin. Annual checkup due in April."},
    {"employee_name": "Bob Smith", "ssn": "234-56-7890", "salary": 132000.00, "medical_notes": "Type 2 diabetes. Takes metformin daily."},
    {"employee_name": "Carol Davis", "ssn": "345-67-8901", "salary": 178000.00, "medical_notes": "No known allergies. Completed physical in January."},
    {"employee_name": "David Wilson", "ssn": "456-78-9012", "salary": 95000.00, "medical_notes": "Asthma. Uses inhaler as needed."},
    {"employee_name": "Emily Chen", "ssn": "567-89-0123", "salary": 210000.00, "medical_notes": "Pregnant, due date August. On modified duty."},
    {"employee_name": "Frank Martinez", "ssn": "678-90-1234", "salary": 118000.00, "medical_notes": "High blood pressure. Monthly monitoring required."},
    {"employee_name": "Grace Kim", "ssn": "789-01-2345", "salary": 165000.00, "medical_notes": "Lactose intolerant. No other conditions."},
    {"employee_name": "Henry Brown", "ssn": "890-12-3456", "salary": 142000.00, "medical_notes": "Recovering from knee surgery. Physical therapy twice weekly."},
    {"employee_name": "Iris Patel", "ssn": "901-23-4567", "salary": 155000.00, "medical_notes": "Seasonal allergies. Takes antihistamines."},
    {"employee_name": "Jack Thompson", "ssn": "012-34-5678", "salary": 128000.00, "medical_notes": "Color blind (red-green). No other conditions."},
]

USERS = [
    {"name": "public_user", "role": "public"},
    {"name": "hr_manager", "role": "internal"},
    {"name": "system_admin", "role": "admin"},
]


def get_public_notes() -> list[dict]:
    """Return public notes seed data."""
    return PUBLIC_NOTES


def get_private_records() -> list[dict]:
    """Return private records seed data."""
    return PRIVATE_RECORDS


def get_users() -> list[dict]:
    """Return users seed data."""
    return USERS


def get_private_employee_names() -> list[str]:
    """Return list of private employee names (used for attack scoring)."""
    return [r["employee_name"] for r in PRIVATE_RECORDS]


def get_private_ssns() -> list[str]:
    """Return list of private SSNs (used for attack scoring)."""
    return [r["ssn"] for r in PRIVATE_RECORDS]


def get_private_salaries() -> list[float]:
    """Return list of private salaries (used for attack scoring)."""
    return [r["salary"] for r in PRIVATE_RECORDS]


def write_seed_files():
    """Write seed data to JSON files for reference."""
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    with open(SEED_DIR / "public_notes.json", "w") as f:
        json.dump(PUBLIC_NOTES, f, indent=2)
    with open(SEED_DIR / "private_records.json", "w") as f:
        json.dump(PRIVATE_RECORDS, f, indent=2)
