from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import EmailField

class RegisterForm(Form):
    firstname = StringField('', [
        validators.DataRequired(),
        validators.Length(min=1, max=20)
    ], render_kw={"placeholder":"First Name"})
    lastname = StringField('', [
        validators.Length(min=1, max=20)
    ], render_kw={"placeholder":"Last Name"})
    username = StringField('', [
        validators.DataRequired(),
        validators.Length(min=4, max=20)
    ], render_kw={"placeholder":"Username"})
    email = EmailField('', [
        validators.DataRequired(),
        validators.Length(min=5, max=50)
    ], render_kw={"placeholder":"Email"})
    password = PasswordField('', [
        validators.DataRequired(),
    ], render_kw={"placeholder":"Password"})
    confirm = PasswordField('', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Password do not match')
    ], render_kw={"placeholder":"Confirm Password"})

class LoginForm(Form):
    username = StringField('', [
        validators.DataRequired(),
        validators.Length(min=4, max=20)
    ], render_kw={"placeholder":"Username"})
    password = PasswordField('', [
        validators.DataRequired(),
    ], render_kw={"placeholder":"Password"})

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])
