from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль повторно', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class AddFilmForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    director = StringField('Режиссер', validators=[DataRequired()])
    image = StringField('Ссылка на изображение', validators=[DataRequired()])
    date = StringField('Премьера')
    time = StringField('Продолжительность')
    description = TextAreaField('Описание')
    submit = SubmitField('Добавить')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    tags = TextAreaField('Теги (Новость, Новинка...)')
    image = StringField('Ссылка на изображение', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class AddServerForm(FlaskForm):
    name = StringField('Имя сервера', validators=[DataRequired()])
    players = StringField('Ссылка для получения текущего онлайна', validators=[DataRequired()])
    url = StringField('Ссылка для быстрого подключения', validators=[DataRequired()])
    description = TextAreaField('Описание (по пунктам, разделитель ";")', validators=[DataRequired()])
    icon = StringField('Иконка (имя файла на сервере)', validators=[DataRequired()])
    img = StringField('Картинка (имя файла на сервере)', validators=[DataRequired()])
    submit = SubmitField('Готово')
