from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
app.secret_key = 'my secretkey'

class blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime(), default = datetime.utcnow)
    content = db.Column(db.Text)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Önce giriş yapmanız gerekiyor.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    posts = blogpost.query.order_by(blogpost.date_posted.desc()).all()
    return render_template('index.html', pagetitle = 'Anasayfa', posts = posts)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Geçersiz kimlik bilgileri. Lütfen tekrar deneyin.'
        else:
            session['logged_in'] = True
            return redirect(url_for('posts'))
    return render_template('login.html', error = error, pagetitle = 'Giriş Yap')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html', pagetitle = 'Hakkımda')

@app.route('/posts')
@login_required
def posts():
    blogposts = blogpost.query.order_by(blogpost.date_posted.desc()).all()
    return render_template('posts.html', pagetitle = 'Yazılar', blogposts = blogposts)

@app.route('/contact')
def contact():
    return render_template('contact.html', pagetitle = 'İletişim')    

@app.route('/post/<int:post_id>')
def post(post_id):
    post = blogpost.query.filter_by(id = post_id).first()
    return render_template('post.html', pagetitle = post.title, post=post)

@app.route('/add')
@login_required
def add():
    return render_template('add.html', pagetitle = 'Yazı Ekle')

@app.route('/addpost', methods = ['GET', 'POST'])
@login_required
def addpost():
    try:
        if request.method == 'POST':
            title = request.form['title']
            subtitle = request.form['subtitle']
            author = request.form['author']
            content = request.form['content']

            post = blogpost(title = title, subtitle = subtitle, author = author, content = content, \
                            date_posted  =  datetime.now())
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))

        else:
            return render_template('404.html', error = str(e))

    except Exception as e:
        return render_template('404.html', error = str(e))

@app.route('/404')
def error_404():
    return render_template('404.html', pagetitle = "Hata!", error = 'Kötü şeylerin peşindesin! Yapma!')

@app.route('/postdelete/<int:post_id>')
@login_required
def postdelete(post_id):
    postdel = blogpost.query.filter_by(id = post_id).first()
    try:
        db.session.delete(postdel)
        db.session.commit()
        return redirect(url_for('index'))

    except Exception as e:
        return render_template('404.html', error = str(e))

@app.route('/postupdate/<int:post_id>')
@login_required
def postupdate(post_id):
    post = blogpost.query.filter_by(id = post_id).first()
    try:
        return render_template('postupdate.html', post_id = post_id, title = post.title, \
                               subtitle = post.subtitle, author = post.author, content = post.content)

    except Exception as e:
        return render_template('404.html', error = str(e))

@app.route('/update', methods = ['GET', 'POST'])
@login_required
def update():
    try:
        pid = request.form['post_id']
        post = blogpost.query.filter_by(id = pid).first()
        if request.method == 'POST':
            post.title = request.form['title']
            post.subtitle = request.form['subtitle']
            post.author = request.form['author']
            post.content = request.form['content']

            db.session.commit()
            return redirect(url_for('index'))

        else:
            return render_template('404.html', error = str(e))

    except Exception as e:
        return render_template('404.html', error = str(e))

if __name__ == '__main__':
    app.run(debug=True)
