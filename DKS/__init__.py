import os
from flask import Flask
from flask import render_template
from flask import session
from flask import redirect
from flask import request
from flask import url_for

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'dks.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # register the database commands
    from . import db
    db.init_app(app)

    # apply the blueprints to the app
    from . import auth
    app.register_blueprint(auth.bp)

    from . import scheduler
    app.register_blueprint(scheduler.bp)

    @app.route('/')
    def index():
        return redirect(url_for('schedule.index'))

    return app
