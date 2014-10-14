import config
import random
from google.appengine.ext import ndb
from base_handler import BaseHandler
from google.appengine.api import users


class Account(ndb.Model):
    api_key_quota = ndb.IntegerProperty(default=config.default_api_key_quota)
    number_of_api_keys = ndb.IntegerProperty(default=0)
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_by_api_key(cls, api_key):
        result = cls.get_by_id(api_key)
        if result:
            return result
        return cls.query(cls.api_key == api_key).get()


class ApiKey(ndb.Model):
    email = ndb.StringProperty()
    label = ndb.StringProperty()
    user_id = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def random_key(length):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(random.choice(chars) for x in xrange(length))

    @classmethod
    def exists(cls, api_key):
        return cls.get_by_id(api_key) and True

    @classmethod
    def unused_api_key(cls):
        new_key = cls.random_key(32)
        while cls.exists(new_key):
            new_key = cls.random_key(32)
        return new_key


class AccountHandler(BaseHandler):
    def get(self):
        user = self.user()
        if user:
            account = Account.get_by_id(user.user_id(), parent=self.root.key)
            if not account:
                account = Account(
                    id=user.user_id(),
                    parent=self.root.key,
                    email=user.email(),
                )
                api_key = ApiKey(
                    id=ApiKey.unused_api_key(),
                    parent=self.root.key,
                    user_id=user.user_id(),
                    email='mail@example.com',
                    label='Default'
                )
                account.number_of_api_keys += 1
                ndb.put_multi([api_key, account])
                api_keys = [{
                    'key': api_key.key.id(),
                    'email': api_key.email,
                    'label': api_key.label,
                }]
            else:
                api_keys = [
                    {
                        'key': k.key.id(),
                        'email': k.email or '',
                        'label': k.label or '',
                    } for k in ApiKey.query(
                        ApiKey.user_id == user.user_id(),
                        ancestor=self.root.key
                    )
                ]
            self.context.update({
                'api_key_quota': account.api_key_quota,
                'number_of_api_keys': account.number_of_api_keys,
                'api_keys': api_keys,
                'email': account.email or '',
                'active_page': 'account',
            })
            return self.render('account.html')
        return self.redirect(self.uri_for('login', _full=True))


class ApiKeyHandler(BaseHandler):

    def post(self):
        user = self.user()
        if not user:
            return self.error(401)
        try:
            label = self.request.get('label').strip()
        except AttributeError:
            label = None
        try:
            recipient = self.request.get('recipient').strip()
        except AttributeError:
            recipient = None
        api_key = self.request.get('api-key').strip()
        api_key = (
            api_key and ndb.Key(
                'PseudoParent', 'root',
                'ApiKey', api_key
            ).get()
        ) or None
        if api_key:
            api_key.email = recipient
            api_key.label = label
            api_key.put()
        else:
            account = Account.get_by_id(user.user_id(), parent=self.root.key)
            if account and account.number_of_api_keys < account.api_key_quota:
                api_key = ApiKey(
                    id=ApiKey.unused_api_key(),
                    parent=self.root.key,
                    user_id=user.user_id(),
                    email=recipient,
                    label=label
                )
                account.number_of_api_keys += 1
                ndb.put_multi([api_key, account])
            else:
                return self.error(400)
        return self.redirect(self.uri_for('account'))


class LoginHandler(BaseHandler):
    def get(self):
        if self.user():
            return self.redirect(self.uri_for('account'))
        else:
            return self.redirect(
                users.create_login_url(self.uri_for('account', _full=True))
            )


class LogoutHandler(BaseHandler):
    def get(self):
        return self.redirect(
            users.create_logout_url(self.uri_for('index', _full=True))
        )
