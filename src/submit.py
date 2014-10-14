import os
import datetime
import webapp2
import config
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from base_handler import BaseHandler


class Submission(ndb.Model):

    api_key = ndb.StringProperty()
    datetime = ndb.DateTimeProperty(auto_now_add=True)
    sender_ip = ndb.StringProperty()
    recipient = ndb.StringProperty()
    form_url = ndb.StringProperty()


class Handler(BaseHandler):

    def post(self):
        api_key = self.request.get('newman_api_key').strip()
        api_key = (
            api_key and ndb.Key(
                'PseudoParent', 'root',
                'ApiKey', api_key
            ).get()
        ) or None
        try:
            referer = os.environ['HTTP_REFERER']
        except KeyError:
            referer = None
        try:
            fields = self.request.get('newman_fields').split(',')
        except AttributeError:
            fields = []
        try:
            required_fields = self.request.get('newman_required').split(',')
        except AttributeError:
            required_fields = []
        return_urls = {
            s: (
                self.request.get(
                    '_'.join(['newman', s, 'url'])
                ).encode('ascii') or
                webapp2.uri_for(s, _full=True, url=referer)
            )
            for s in ['thanks', 'sorry', 'oops']
        }
        if not all([
            api_key,
            fields,
            all([f in fields for f in required_fields])
        ]):
            return self.redirect(return_urls['sorry'])
        payload = {
            f: self.request.get(f) or '' for f in fields
        }
        if not all([
            v.strip() for k, v in payload.items() if k in required_fields
        ]):
            return self.redirect(return_urls['oops'])
        recipient = api_key.email
        taskqueue.add(
            url=webapp2.uri_for('queue.send_email'),
            params={
                'recipient': recipient,
                'subject': config.email_subject,
                'body': self.jinja.get_template('email.txt').render(
                    {
                        'referer': referer,
                        'now': datetime.datetime.now().isoformat(' '),
                        'payload': payload,
                    }
                ),
            }
        )
        Submission(
            form_url=referer,
            api_key=api_key.key.id(),
            sender_ip=self.request.remote_addr,
            recipient=recipient,
        ).put()
        return self.redirect(return_urls['thanks'])
