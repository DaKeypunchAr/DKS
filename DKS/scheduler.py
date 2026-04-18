from flask import Blueprint
from flask import session
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request

from .db import get_db
from .auth import login_required

from datetime import datetime

bp = Blueprint("schedule", __name__, url_prefix="/schedule")

@bp.route('/')
@login_required
def index(user):
    unfinished_task_list = get_db().execute('SELECT * FROM task WHERE user_id = ? AND completed = 0 ORDER BY priority DESC',
                           (user['id'],)).fetchall()
    finished_task_list = get_db().execute('SELECT * FROM task WHERE user_id = ? AND completed = 1 ORDER BY completion_time DESC',
                                          (user['id'],)).fetchall()
    return render_template('schedule/index.html', username = user['username'], unfinished_tasks = unfinished_task_list, finished_tasks = finished_task_list)

@bp.route('/add_task', methods=('GET', 'POST'))
@login_required
def add_task(user):
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
        db.execute('INSERT INTO task (title, description, priority, user_id) VALUES (?, ?, ?, ?)', (task_title, description, priority, user['id']))
        db.commit()
        return redirect(url_for('schedule.index'))

    return redirect(url_for('schedule.add_task'))

@bp.route('/task', methods=('GET', 'POST'))
@login_required
def task_details(user):
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    db = get_db()
    task = db.execute('SELECT * FROM task WHERE id = ?', (tid,)).fetchone()
    return render_template('schedule/task.html', task=task)

@bp.get('/remove_task')
@login_required
def remove_task(user):
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    db = get_db()
    db.execute('DELETE FROM task WHERE id = ?', (tid,))
    db.commit()
    return redirect(url_for('schedule.index'))

@bp.route('/edit_task', methods=('GET', 'POST'))
@login_required
def edit_task(user):
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
@login_required
def toggle_task_completion(user):
    tid = request.args.get('tid')
    if tid is None:
        return redirect(url_for('schedule.index'))

    db = get_db()
    completed = db.execute('SELECT * FROM task WHERE id = ?',
                           (tid,)).fetchone()['completed']

    completed = 1 if completed == 0 else 0
    db.execute('UPDATE task SET completed = ?, completion_time = ? WHERE id = ?', (completed, datetime.now() if completed else None, tid))

    db.commit()
    return redirect(url_for('schedule.task_details', tid=tid))
