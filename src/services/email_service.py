import smtplib
from email.message import EmailMessage
from typing import List

class EmailConfig:
    def __init__(self):
        self.smtp_server = ""
        self.smtp_port = 587
        self.sender_email = ""
        self.password = ""
        self.use_tls = True

class EmailService:
    def __init__(self, config: EmailConfig):
        self.config = config

    def send_alert(self, to_emails: List[str], subject: str, content: str) -> bool:
        if not self.config.smtp_server or not self.config.sender_email:
            print("Email settings are not configured.")
            return False
            
        if not to_emails:
            return False

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.config.sender_email
        msg['To'] = ", ".join(to_emails)
        msg.set_content(content)

        try:
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                if self.config.password:
                    server.login(self.config.sender_email, self.config.password)
                
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False
