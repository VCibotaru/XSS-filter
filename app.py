from flask import Flask

from vuln import vuln_blueprint


def create_app():
    # configuring stuff
    app = Flask(__name__)
    app.debug = True
    app.register_blueprint(vuln_blueprint)
    return app
