from base_handler import BaseHandler


class Handler(BaseHandler):

    def get(self, page):
        self.context.update({
            'active_page': page,
        })
        return self.render('.'.join([page, 'html']))
