from flask import current_app as app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from tsdip.constants import EmailTemplate


class SendGrid():
    """Sendgrid function."""

    api_key = app.config['SENDGRID_API_KEY']
    sender = app.config['SYSTEM_SENDER']

    def __init__(self):
        """Sendgrid constructor."""
        self.sg = SendGridAPIClient(self.api_key)

    def send(self, to_emails, email_type='SYSTEM', params={}):
        """Sendgrid sending function."""
        if len(to_emails) < 1:
            return False

        message = Mail(
            from_email=self.sender,
            to_emails=to_emails,
        )

        if email_type not in EmailTemplate.__members__:
            return False
        message.template_id = EmailTemplate[email_type].value
        message.dynamic_template_data = params

        response = self.sg.send(message)
        res = {
            'body': response.body,
            'headers': response.headers,
            'status': response.status_code,
        }
        app.logger.debug(f'sendgrid_send_result {res}')
        return res
