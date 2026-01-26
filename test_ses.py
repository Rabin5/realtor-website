import smtplib

# Replace with your SES SMTP credentials
SMTP_USERNAME = "AKIAWZNJ5JIP6ZUKCDKP"
SMTP_PASSWORD = "BPUWHxDARHKjpZI5U44z5TGpwH7AEH3OxW2YYHrtZaQU"

# SES SMTP server (region: us-east-1)
SMTP_HOST = "email-smtp.us-east-1.amazonaws.com"
SMTP_PORT = 587

try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()  # Enable TLS
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    print("Login SUCCESS! SES SMTP credentials are correct.")
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print("Login FAILED! Check SMTP credentials.")
    print(e)


