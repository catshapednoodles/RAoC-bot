# import the modules
import logging
import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap4
from waitress import serve

import posts as db

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bootstrap = Bootstrap4(app)
app._static_folder = os.path.abspath("templates/static/")

recent_error = ""

RUNNING_IN_DOCKER = os.environ.get('RUNNING_IN_DOCKER', False)
USE_PROXY = os.environ.get('USE_PROXY', False)


@app.route("/")
def show_posts():
    global recent_error
    try:
        data = db.get_posts()
        return render_template('posts.html', data=data, recent_error=recent_error)
    except Exception as e:
        print(repr(e))
        recent_error = repr(e)
        return recent_error


def clear_recent_error():
    global recent_error
    recent_error = ""


def initialize_db_and_values():
    db.create_database_and_tables()


if __name__ == '__main__':
    logging.info("Initializing database")
    initialize_db_and_values()

    if RUNNING_IN_DOCKER:
        if USE_PROXY:
            logging.info("Starting web app in a Docker environment behind reverse proxy")
            from werkzeug.middleware.proxy_fix import ProxyFix

            app.wsgi_app = ProxyFix(
                app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
            )

            serve(app, port=5000, host="0.0.0.0")
        else:
            logging.info("Starting web app in a Docker environment")
            serve(app, port=5000, host="0.0.0.0")
    else:
        logging.info("Starting web app on local machine")
        app.run(port=80)
