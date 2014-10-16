from flask.ext.script import Manager

from app import create_app


app = create_app()
manager = Manager(app)


@manager.command
def run(debug=False):
    """Run in local machine."""
    if debug:
        app.debug = True
        app.run(host='127.0.0.1', port=8000)
    else:
        app.run(host='0.0.0.0', port=8000)


if __name__ == "__main__":
    manager.run()
