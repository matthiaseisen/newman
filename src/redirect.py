import webapp2
from base_handler import BaseHandler


class Handler(BaseHandler):

    def get(self, page):
        self.context.update({
            'active_page': page,
            'url': (
                self.request.get('url') or
                webapp2.uri_for('index')
            )
        })
        return self.render('.'.join([page, 'html']))
