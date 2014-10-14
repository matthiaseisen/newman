import webapp2
import urllib
import base64
import config
from google.appengine.api import urlfetch


class SendEmail(webapp2.RequestHandler):

    def post(self):
        self.request.get('key')
        fields = {
            'from': '%s <%s>' % (
                config.mailgun_sender_name,
                config.mailgun_sender_email
            ),
            'to': self.request.get('recipient'),
            'subject': self.request.get('subject'),
            'text': self.request.get('body'),
        }
        payload = urllib.urlencode(fields)
        result = urlfetch.fetch(
            url=config.mailgun_api_url,
            payload=payload,
            method=urlfetch.POST,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic %s' % base64.b64encode(
                    'api:%s' % config.mailgun_api_key
                ),
            }
        )
        return self.error(result.status_code)
