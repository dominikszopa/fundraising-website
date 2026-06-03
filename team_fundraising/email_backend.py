"""
Custom Django email backend that delegates to AWS SES via send_email().
"""
from django.core.mail.backends.base import BaseEmailBackend

from .email_utils import send_email


class SESEmailBackend(BaseEmailBackend):
    """Routes Django's built-in email sending (e.g. password reset) through SES."""

    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            html_content = None
            for content, mimetype in getattr(message, 'alternatives', []):
                if mimetype == 'text/html':
                    html_content = content
                    break

            success = send_email(
                subject=message.subject,
                text_content=message.body,
                from_email=message.from_email,
                to_emails=message.to,
                html_content=html_content,
            )
            if success:
                sent += 1
        return sent
