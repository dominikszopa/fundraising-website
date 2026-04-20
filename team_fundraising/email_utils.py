"""
Email sending utilities using AWS SES
"""
import boto3
from botocore.exceptions import ClientError
import logging
from django.conf import settings

from .text import Donation_text

logger = logging.getLogger(__name__)


def send_email(subject, text_content, from_email, to_emails, html_content=None):
    """
    Send email using AWS SES

    Args:
        subject: Email subject line
        text_content: Plain text email body
        from_email: Sender email address
        to_emails: List of recipient email addresses
        html_content: Optional HTML email body

    Returns:
        True if successful, False otherwise
    """
    # Check if AWS credentials are configured
    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        logger.debug(
            f"AWS SES credentials not configured. "
            f"Email to {to_emails} not sent (dev/test environment)"
        )
        return False

    # Create SES client
    ses_client = boto3.client(
        'ses',
        region_name=settings.AWS_SES_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    # Build email body
    body = {'Text': {'Data': text_content, 'Charset': 'UTF-8'}}
    if html_content:
        body['Html'] = {'Data': html_content, 'Charset': 'UTF-8'}

    try:
        response = ses_client.send_email(
            Source=from_email,
            Destination={'ToAddresses': to_emails},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': body
            }
        )
        logger.info(
            f"Email sent successfully to {to_emails}. "
            f"MessageId: {response['MessageId']}"
        )
        return True

    except ClientError as e:
        logger.error(
            f"Failed to send email to {to_emails}: "
            f"{e.response['Error']['Message']}"
        )
        return False
    except Exception as e:
        logger.error(
            f"Failed to send email to {to_emails}: "
            f"{type(e).__name__}: {str(e)}"
        )
        return False


def send_donation_emails(donation):
    """Send the donor thank-you and the fundraiser-notification emails.

    Extracted from paypal.py::process_paypal so the Advanced Checkout
    capture view and webhook can reuse it. Safe to call more than once,
    but callers should guard with an idempotent status transition to
    avoid duplicate sends.
    """
    amount_str = '${:,.2f}'.format(donation.amount)

    thank_you_text = (
        Donation_text.confirmation_email_opening
        + amount_str + ' to '
        + donation.fundraiser.name
        + Donation_text.confirmation_email_closing_text
    )
    thank_you_html = (
        Donation_text.confirmation_email_opening
        + amount_str + ' to '
        + donation.fundraiser.name
        + Donation_text.confirmation_email_closing_html
    )
    send_email(
        Donation_text.confirmation_email_subject,
        thank_you_text,
        settings.DEFAULT_FROM_EMAIL,
        [donation.email],
        html_content=thank_you_html,
    )

    if donation.fundraiser and donation.fundraiser.user:
        notification_text = (
            Donation_text.notification_email_opening
            + amount_str + ' from '
            + donation.name + " <" + donation.email + ">"
            + ' with the message:\n\n"' + donation.message + '"'
            + Donation_text.notification_email_closing
        )
        send_email(
            Donation_text.notification_email_subject,
            notification_text,
            settings.DEFAULT_FROM_EMAIL,
            [donation.fundraiser.user.email],
        )
