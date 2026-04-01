import os
from flask import Flask
from flask import render_template
from flask import session
from flask import redirect
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

    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        user_id = session['user_id']

        from .db import get_db
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = ?',
                          (user_id,)).fetchone()

        if user is None:
            session.clear()
            return redirect(url_for('auth.login'))

        name = user['username']
        return render_template('index.html', username = name, tasks = [])

    @app.route('/add_task')
    def add_task():
        return render_template('add_task.html')

    return app
