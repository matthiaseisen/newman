import os
import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import config


class PseudoParent(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class BaseHandler(webapp2.RequestHandler):

    def __init__(self, request, response):
        self.context = {
            'static_url': config.static_url,
            'meta_title': config.meta_title,
            'meta_keywords': config.meta_keywords,
            'meta_description': config.meta_description,
            'ga_id': config.ga_id,
            'contact_api_key': config.contact_api_key,
        }
        self.root = PseudoParent.get_or_insert('root')
        self.jinja = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                '/'.join([
                    os.path.dirname(__file__).rstrip('/'),
                    'templates'
                ])
            )
        )
        webapp2.RequestHandler.__init__(self, request, response)

    def render(self, tpl):
        self.response.write(self.jinja.get_template(tpl).render(self.context))

    def user(self):
        return users.get_current_user()
