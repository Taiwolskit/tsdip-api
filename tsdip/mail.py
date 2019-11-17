from flask import current_app as app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from tsdip.constants import EmailTemplate


class SendGrid():
    api_key = app.config['SENDGRID_API_KEY']
    sender = app.config['SYSTEM_SENDER']

    def __init__(self):
        self.sg = SendGridAPIClient(self.api_key)

    def send(self, to_emails, email_type='SYSTEM', params={}):
        message = Mail(
            from_email=self.sender,
            to_emails=to_emails,
        )

        message.template_id = EmailTemplate[email_type].value
        message.dynamic_template_data = params

        try:
            response = self.sg.send(message)
            res = {
                'body': response.body,
                'headers': response.headers,
                'status': response.status_code,
            }
        except Exception as err:
            res = {
                'code': 'ERROR_MANAGER_2',
                'description': str(err),
                'status': 'ERROR',
            }
        finally:
            app.logger.debug(f'sendgrid_send_result {res}')
            return res
