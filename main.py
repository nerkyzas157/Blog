import os
from datetime import datetime
from flask import Flask, abort, render_template, redirect, url_for, flash, request  # type: ignore
from flask_bootstrap import Bootstrap5  # type: ignore
from flask_ckeditor import CKEditor  # type: ignore
from flask_gravatar import Gravatar  # type: ignore
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column  # type: ignore
from sqlalchemy import Integer, String, Text, ForeignKey  # type: ignore
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
import smtplib

from forms import CreatePostForm, CommentForm, LoginForm, RegisterForm


SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
APP_PASSWORD = os.environ.get("SMTP_APP_PASS")


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            return fn(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function


gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None,
)


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    comments = relationship("Comment", back_populates="comment_author")
    posts = relationship("BlogPost", back_populates="author")


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


@app.route("/register")
def register():
    form = RegisterForm()
    return render_template("register.html", form=form)


@app.route("/register", methods=["POST"])
def register_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if user:
        flash("Email address already exists")
        return redirect(url_for("register"))
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        ),
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    return redirect(url_for("get_all_posts"))


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    if not user:
        flash("That email does not exist, please try again.")
        return redirect(url_for("login"))
    elif not check_password_hash(user.password, password):
        flash("Password incorrect, please try again.")
        return redirect(url_for("login"))
    else:
        login_user(user)
        return redirect(url_for("get_all_posts"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


@app.route("/")
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in to comment.")
            return redirect(url_for("login"))
        new_comment = Comment(
            author_id=current_user.id,
            post_id=post_id,
            text=form.text.data,
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))
    return render_template("post.html", post=requested_post, form=form)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if request.method == "POST" and form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=datetime.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_message = f"Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:{message}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(SMTP_EMAIL, APP_PASSWORD)
        connection.sendmail(SMTP_EMAIL, SMTP_EMAIL, email_message)


if __name__ == "__main__":
    app.run(debug=False)
