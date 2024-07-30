from flask_wtf import FlaskForm  # type: ignore
from wtforms import StringField, PasswordField, SubmitField, EmailField  # type: ignore
from wtforms.validators import DataRequired, URL  # type: ignore
from flask_ckeditor import CKEditorField  # type: ignore


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email Address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    text = CKEditorField("Your Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
