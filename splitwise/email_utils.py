# email_utils.py

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import List


def send_expense_notification(
    recipient: str,
    total_amount_owed: float,
):
    # email configuration
    smtp_server = ""
    smtp_port = 587
    sender_email = ""
    sender_password = ""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = "Expense Notification"

    body = (
        f"Dear User,\n\n"
        f"You have been added to a new expense.\n"
        f"Total amount you owe for this expense: {total_amount_owed}\n"
        f"Best regards,\nYour Expense Management Team"
    )

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
