
"""Loan eligibility and repayment calculator."""

import json
import os
import smtplib
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage

import paramiko


APPLICATIONS = {}
MAX_FOIR = 0.50
BUREAU_HOST = os.getenv("BUREAU_HOST", "ftp.creditbureau.example")
ALLOWED_LOAN_TYPES = {"home", "car", "personal"}


def calculate_emi(principal, annual_rate, years):
    """Calculate monthly EMI. Annual rate is expressed as a percentage."""
    if principal <= 0 or years <= 0 or annual_rate < 0:
        raise ValueError(
            "Principal and years must be positive; rate cannot be negative.")

    months = years * 12
    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        return principal / months

    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)


def check_eligibility(
    age, income, credit_score, existing_emi, loan_type, history=None
):
    """Check an applicant against basic loan eligibility rules."""
    if history is None:
        history = []

    history.append(loan_type)

    if not 21 <= age <= 60:
        return False
    if income <= 0 or existing_emi < 0:
        return False
    if loan_type not in ALLOWED_LOAN_TYPES:
        return False
    if not 300 <= credit_score <= 850 or credit_score < 650:
        return False
    if existing_emi / income > MAX_FOIR:
        return False

    return True


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Estimate the maximum principal affordable under the FOIR limit."""
    if income <= 0 or existing_emi < 0 or years <= 0:
        raise ValueError(
            "Income and years must be positive; EMI cannot be negative.")

    available_payment = income * MAX_FOIR - existing_emi
    if available_payment <= 0:
        return 0.0

    months = years * 12
    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        return available_payment * months

    return available_payment * (
        1 - (1 + monthly_rate) ** (-months)
    ) / monthly_rate


def amortisation_schedule(principal, annual_rate, years):
    """Return monthly interest and remaining balance for a loan."""
    emi = calculate_emi(principal, annual_rate, years)
    monthly_rate = annual_rate / 100 / 12
    balance = principal
    rows = []

    for month in range(1, years * 12 + 1):
        interest = balance * monthly_rate
        balance = max(0.0, balance - (emi - interest))
        rows.append((month, round(interest, 2), round(balance, 2)))

    return rows


def application_id():
    """Generate a unique application identifier."""
    return f"LN-{uuid.uuid4().hex[:12].upper()}"


def save_application(name, amount, file="loans.json"):
    """Save application records in JSON format."""
    if not name.strip() or amount <= 0:
        raise ValueError("Applicant name and amount must be valid.")

    app_id = application_id()
    APPLICATIONS[app_id] = {
        "name": name,
        "amount": amount,
        "date": datetime.now(timezone.utc).isoformat(),
    }

    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(APPLICATIONS, output_file, indent=2)

    return app_id


def load_applications(file="loans.json"):
    """Load and validate application records from a JSON file."""
    global APPLICATIONS

    try:
        with open(file, "r", encoding="utf-8") as input_file:
            records = json.load(input_file)
    except FileNotFoundError:
        APPLICATIONS = {}
        return

    if not isinstance(records, dict):
        raise ValueError("Application data must be a JSON object.")

    if not all(
        isinstance(key, str) and isinstance(value, dict)
        for key, value in records.items()
    ):
        raise ValueError("Invalid application record format.")

    APPLICATIONS = records


def upload_to_bureau(report_path, user=None, password=None):
    """Upload a report securely using SFTP."""
    user = user or os.getenv("BUREAU_USER")
    password = password or os.getenv("BUREAU_PASSWORD")

    if not user or not password:
        raise ValueError("Set BUREAU_USER and BUREAU_PASSWORD first.")

    host = os.getenv("BUREAU_HOST")
    if not host:
        raise ValueError("Set BUREAU_HOST to the SFTP server hostname.")

    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.connect(
            hostname=host,
            username=user,
            password=password,
            timeout=10,
        )

        with ssh.open_sftp() as sftp:
            sftp.put(
                report_path,
                os.path.basename(report_path),
            )


def notify_applicant(email, status):
    """Send a notification using an authenticated SMTP server."""

    if not email.strip() or "\n" in email or "\r" in email:
        raise ValueError("Invalid email address.")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", smtp_user or "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_host or not smtp_user or not smtp_password or not sender:
        raise ValueError(
            "Configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM.")

    message = EmailMessage()
    message["Subject"] = f"Loan {status}"
    message["From"] = sender
    message["To"] = email
    message.set_content(f"Your loan application status is: {status}")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)


def interest_saved(principal, annual_rate, years, prepayment):
    """Estimate interest savings from an immediate principal prepayment."""
    if prepayment < 0 or prepayment >= principal:
        raise ValueError(
            "Prepayment must be non-negative and below principal.")

    original_total = calculate_emi(principal, annual_rate, years) * years * 12
    reduced_total = (
        calculate_emi(principal - prepayment, annual_rate, years)
        * years
        * 12
    )
    return original_total - reduced_total


def risk_band(credit_score):
    """Return a risk category for a credit score."""
    if not 300 <= credit_score <= 850:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    return "VERY HIGH"


def main():
    """Run example calculations and demonstrate application storage."""
    print("EMI for 5L at 9% for 5 years:",
          round(calculate_emi(500000, 9, 5), 2))
    print(
        "Eligible (score 760):",
        check_eligibility(35, 40000, 760, 5000, "personal"),
    )
    print(
        "Eligible (unknown loan type):",
        check_eligibility(30, 80000, 650, 0, "crypto"),
    )
    print("Max loan for income 40000:", round(
        max_loan_amount(40000, 5000, 9, 5), 2))
    print("Last schedule row:", amortisation_schedule(100000, 12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print("Interest saved:", round(interest_saved(500000, 9, 5, 50000), 2))

    app_id = save_application("Anil", 500000)
    load_applications()
    print("Saved application:", app_id)
    print("Applications on file:", len(APPLICATIONS))
    print("Bureau upload skipped (no network).")


if __name__ == "__main__":
    main()
