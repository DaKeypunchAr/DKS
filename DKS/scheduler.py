from flask import Blueprint
from flask import session
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request

from .db import get_db
bp = Blueprint("schedule", __name__, url_prefix="/schedule")

@bp.route('/')
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
    task_list = db.execute('SELECT * FROM task WHERE user_id = ?',
                           (user_id,)).fetchall()
    return render_template('schedule/index.html', username = name, tasks = task_list)

@bp.route('/add_task', methods=('GET', 'POST'))
def add_task():
    if request.method == 'GET':
        return render_template('schedule/add_task.html')

    task_title = request.form['title']
    description = request.form['description']
    priority = request.form['priority']

    error = None

    if not task_title:
        error = 'Title is required!'
        flash(error)
    else:
        try:
            priority = int(priority)
        except:
            error = 'Priority should be an integer!'
            flash(error)

    if error is None:
        db = get_db()
        db.execute('INSERT INTO task (title, description, priority, user_id) VALUES (?, ?, ?, ?)', (task_title, description, priority, session['user_id']))
        db.commit()
        return redirect(url_for('schedule.index'))

    return redirect(url_for('schedule.add_task'))

@bp.route('/task', methods=('GET', 'POST'))
def task_details():
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    db = get_db()
    task = db.execute('SELECT * FROM task WHERE id = ?', (tid,)).fetchone()
    return render_template('schedule/task.html', task=task)

@bp.get('/remove_task')
def remove_task():
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (tid,))
    db.commit()
    return redirect(url_for('schedule.index'))

@bp.route('/edit_task', methods=('GET', 'POST'))
def edit_task():
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    if request.method == 'GET':
        db = get_db()
        task = db.execute('SELECT * FROM task WHERE id = ?', (tid,)).fetchone()
        return render_template('schedule/edit_task.html', task = task)

    task_title = request.form['title']
    description = request.form['description']
    priority = request.form['priority']

    error = None

    if not task_title:
        error = 'Title is required!'
        flash(error)
    else:
        try:
            priority = int(priority)
        except:
            error = 'Priority should be an integer!'
            flash(error)

    if error is None:
        db = get_db()
        db.execute('UPDATE task SET title = ?, description = ?, priority = ? WHERE id = ?', (task_title, description, priority, tid))
        db.commit()
        return redirect(url_for('schedule.index'))

    return redirect(url_for('schedule.edit_task', tid=tid))


@bp.get('/toggle_task_completion')
def toggle_task_completion():
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    db = get_db()
    completed = db.execute('SELECT * FROM task WHERE id = ?',
                           (tid,)).fetchone()['completed']
    print(completed)
    db.execute('UPDATE task SET completed = ? WHERE id = ?', (1 if
        completed == 0 else 0, tid))
    db.commit()
    return redirect(url_for('schedule.task_details', tid=tid))
