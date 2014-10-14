import config
import webapp2
import routes

app = webapp2.WSGIApplication(
    routes.routes,
    debug=config.debug
)

if __name__ == '__main__':
    app.run()
