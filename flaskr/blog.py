from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username '
        ' FROM post p JOIN user u ON p.author_id = u.id '
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        db = get_db()
        print(request)
        title = request.form['title']
        body = request.form['body']
        author_id = g.user['id']
        error = None

        if not title:
            error = 'Title is required'
        elif not body:
            error = 'Body is required'

        if error is not None:
            flash(error)
        else:
            new_post = db.execute(
                """INSERT INTO post (title, body, author_id)
                VALUES (?, ?, ?)""", (title, body, author_id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT * FROM post WHERE id = ?", (id,)
    ).fetchone()

    if post is None:
        abort(404, 'ERROR: Post {id} not found.')
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
        
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    print(f"POST: {post}")

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'
        if not body:
            error = 'Body is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            update_query = db.execute(
                "UPDATE post SET title = ?, body = ? WHERE post.id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    db.execute(
        "DELETE FROM post WHERE id = ?", (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))