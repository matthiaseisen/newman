import webapp2
import account
import submit
import redirect
import static
from send_email import SendEmail

routes = [
    webapp2.Route(
        '/',
        handler=static.Handler,
        name='index',
        defaults={'page': 'index'}
    ),
    webapp2.Route(
        '/_ah/queue/send_email',
        handler=SendEmail,
        name='queue.send_email'
    ),
    webapp2.Route('/login/', handler=account.LoginHandler, name='login'),
    webapp2.Route('/logout/', handler=account.LogoutHandler, name='logout'),
    webapp2.Route(
        '/account/',
        handler=account.AccountHandler,
        name='account'
    ),
    webapp2.Route(
        '/sorry/',
        handler=redirect.Handler,
        name='sorry',
        defaults={'page': 'sorry'}
    ),
    webapp2.Route(
        '/oops/',
        handler=redirect.Handler,
        name='oops',
        defaults={'page': 'oops'}
    ),
    webapp2.Route(
        '/thanks/',
        handler=redirect.Handler,
        name='thanks',
        defaults={'page': 'thanks'}
    ),
    webapp2.Route(
        '/docs/',
        handler=static.Handler,
        name='docs',
        defaults={'page': 'docs'}
    ),
    webapp2.Route(
        '/support/',
        handler=static.Handler,
        name='ask',
        defaults={'page': 'ask'}
    ),
    webapp2.Route(
        '/privacy/',
        handler=static.Handler,
        name='privacy',
        defaults={'page': 'privacy'}
    ),
    webapp2.Route('/api-key/', handler=account.ApiKeyHandler, name='api_key'),
    webapp2.Route('/submit/', handler=submit.Handler, name='submit'),
]
