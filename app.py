from flask import Flask
from markupsafe import escape
from flask import url_for, render_template, request, flash, logging, redirect, session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 
import json
from functools import wraps
import forms
app = Flask(__name__)

with open('config.json') as config_file:
    config_data = json.load(config_file)

db_settings = config_data['database']

app.config.update(db_settings)

mysql = MySQL(app)

RegisterForm = forms.RegisterForm
LoginForm = forms.LoginForm
ArticleForm = forms.ArticleForm

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    cur.close()
    return render_template('articles.html', articles=articles)

@app.route('/article/<string:id>')
def article(id):
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    article = cur.fetchone()
    cur.close()
    return render_template('article.html', article=article)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(firstname, lastname, email, username, password) VALUES(%s, %s, %s, %s)", (firstname, lastname, email, username, password))
        
        mysql.connection.commit()

        cur.close()

        flash('You are now registered and can log in', 'success')
        
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        password_candidate = form.password.data

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)     
        else:
            error = 'User not found'
            return render_template('login.html', error=error)
        cur.close()   
    
    return render_template('login.html', form=form)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized login, please login again!', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    # for article in articles:
    #     app.logger.info("body %s", article['body'])
    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No articles found!'
        return render_template('dashboard.html', msg=msg)

    cur.close()

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    
    return render_template('add_article.html', form=form)


@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    article = cur.fetchone()
    cur.close()

    form = ArticleForm(request.form)
    form.title.data = article['title']
    form.body.data = article['body']        

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur = mysql.connection.cursor()

        cur.execute("UPDATE articles SET title = %s, body = %s WHERE id = %s", (title, body, id))
        mysql.connection.commit()
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    
    return render_template('edit_article.html', form=form)

@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.secret_key = config_data['keys']['secret_key']
    app.run(debug=True)
