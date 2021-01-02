import os
import sys
import json
import datetime
import requests
import urllib.request
from bs4 import BeautifulSoup
from random import randint
from flask import Flask
from flask import jsonify, redirect, render_template, session, request
from flask_restful import reqparse, abort, Api, Resource
from Forms import LoginForm, RegistrationForm, AddFilmForm, AddNewsForm, AddServerForm
from db import UsersModel, FilmsModel, NewsModel

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'TimelessRP'
USERS, FILMS, NEWS = UsersModel(), FilmsModel(), NewsModel()
today = datetime.datetime.today()
# NEWS.make_table()
# USERS.make_admin(9)
# FILMS.make_table()
# USERS.make_table()
# USERS.insert('222', '333', 'admin')
# USERS.task()


def abort_if_films_not_found(id):
    if not FILMS.get(id):
        abort(404, message="Films {} not found".format(id))


def beautiful_tags(s:str):
    res = s.split(',')
    for i in range(len(res)):
        res[i] = '_'.join(res[i].split())
        if res[i][0] != '#':
            res[i] = '#' + res[i]
    return res


def check_admin(_id):
    with open(os.path.join(sys.path[0], "admins.txt"), "r", encoding='UTF-8') as f:
        data = list(map(int, f.readlines()))
    print(data)
    if _id in data:
        return True
    return False


def get_cur_online(url):
    if ('https://' or 'http://') not in url:
        return 'error'
    response = requests.get(url, verify=False)
    # webContent = response.read()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.find_all('b')[5].text


@app.route('/')
@app.route('/index')
def home():
    if 'success' not in session:
        return render_template('index.html')
    s = [session['success']]
    session.pop('success', 0)
    return render_template('index.html')


@app.route('/news')
def news():
    news = list(map(list, NEWS.get_all(order='date', limit=10)))
    for n in news:
        n[2] = beautiful_tags(n[2])
    print(news)
    if 'user_id' in session:
        if check_admin(session['user_id']):
            return render_template('news.html', title='Новости', news=news, admin='True')
    return render_template('news.html', title='Новости', news=news, admin='False')


@app.route('/servers')
def servers():
    with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
        data = json.load(f)
    res = []
    for i in data['list']:
        online = get_cur_online(i['url_for_online'])
        res.append([i['id'], i['name'], online, i['card_img']])
    print(res)
    if 'user_id' in session:
        if check_admin(session['user_id']):
            return render_template('servers.html', serv_list=res, admin='True')
    return render_template('servers.html', serv_list=res, admin='False')


@app.route('/servers/<int:id>', methods=['GET', 'POST'])
def server(id):
    with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
        data = json.load(f)
    res = []
    for i in data['list']:
        if i['id'] == id:
            res.append([i['name'], get_cur_online(i['url_for_online']), i['description_list'], i['main_img'], i['url_to_connect']])
    return render_template('server_info.html', info=res[0])


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        exists = USERS.exists(form.username.data)
        if exists[0]:
            if exists[1][2] == form.password.data:
                session['username'] = form.username.data
                session['user_id'] = exists[1][0]
                session['success'] = 'Успешно'
                return redirect('/')
            else:
                form.password.errors = ['Неверный пароль']
        else:
            form.username.errors = ['Пользователь не найден']
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        exists = USERS.exists(form.username.data)
        if exists[0]:
            form.username.errors = ['Пользователь с таким именем уже существует']
        else:
            if form.password.data == form.password_again.data:
                USERS.insert(form.username.data, form.password.data, 'user')
                exists = USERS.exists(form.username.data)
                session['username'] = form.username.data
                session['user_id'] = exists[1][0]
                session['success'] = 'Успешно'
                return redirect('/')
            else:
                form.password.errors = ['Пароли не совпадают']
    return render_template('registration.html', title='Авторизация', form=form)


@app.route('/account')
def account():
    user = USERS.get(session['user_id'])
    if check_admin(session['user_id']):
        user[3] = 'admin'
    else:
        user[3] = 'user'
    print(user)
    return render_template('account.html', user=user)


@app.route('/make_admin', methods=['POST', 'GET'])
def make_admin():
    print(request.form.get('id'))
    USERS.make_admin(request.form.get('id'))
    with open(os.path.join(sys.path[0], "admins.txt"), "w", encoding='UTF-8') as f:
        f.write(request.form.get('id'))
    return redirect('/account')


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/add_news', methods=['POST', 'GET'])
def add_news():
    if 'user_id' in session:
        if check_admin(session['user_id']):
            form = AddNewsForm()
            if form.validate_on_submit():
                NEWS.insert(form.title.data, form.content.data, form.tags.data, form.image.data, today.strftime("%Y-%m-%d;%H.%M.%S"))
            return render_template('add_news.html', title='Добавление новости', form=form)
    return redirect('/')


@app.route('/add_server', methods=['POST', 'GET'])
def add_server():
    if 'user_id' in session:
        if check_admin(session['user_id']):
            form = AddServerForm()
            if form.validate_on_submit():
                descr = form.description.data.split(';')
                data = {'id': randint(0, 1000000),
                        'name': form.name.data,
                        'url_for_online': form.players.data,
                        'url_to_connect': form.url.data,
                        'description_list': descr,
                        'card_img': form.icon.data,
                        'main_img': form.img.data}
                with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
                    j = json.load(f)
                j['list'].insert(0, data)
                with open(os.path.join(sys.path[0], "servers.json"), "w", encoding='UTF-8') as out:
                    json.dump(j, out)
                return redirect('/servers')
            return render_template('add_server.html', form=form)
    return redirect('/')


@app.route('/edit_server/<int:id>', methods=['POST', 'GET'])
def edit_server(id):
    if 'user_id' in session:
        if check_admin(session['user_id']):
            with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
                j = json.load(f)
            for i in range(len(j['list'])):
                if j['list'][i]['id'] == id:
                    data = j['list'][i]
            form = AddServerForm()
            form.name.data, form.players.data, form.url.data, form.description.data, form.icon.data, form.img.data = data['name'], data['url_for_online'], data['url_to_connect'],';'.join(data['description_list']), data['card_img'], data['main_img']
            # print(form.data)
            if request.method == 'POST':
                print(request.form.get('name'))
                descr = request.form.get('description').split(';')
                data1 = {'name': request.form.get('name'),
                         'url_for_online': request.form.get('players'),
                         'url_to_connect': request.form.get('url'),
                         'description_list': descr,
                         'card_img': request.form.get('icon'),
                         'main_img': request.form.get('img')}
                for i in range(len(j['list'])):
                    if j['list'][i]['id'] == id:
                        j['list'][i].update(data1)
                with open(os.path.join(sys.path[0], "servers.json"), "w", encoding='UTF-8') as out:
                    json.dump(j, out)
                return redirect('/servers')
            return render_template('edit_server.html', id1=id, form=form)


@app.route('/del_news/<int:id>', methods=['POST', 'GET'])
def del_news(id):
    NEWS.delete(id)
    return redirect('/')


@app.route('/del_server/<int:id>', methods=['POST', 'GET'])
def del_server(id):
    with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
        j = json.load(f)
    for i in range(len(j['list'])):
        if j['list'][i]['id'] == id:
            j['list'].pop(i)
            break
    with open(os.path.join(sys.path[0], "servers.json"), "w", encoding='UTF-8') as out:
        json.dump(j, out)
    return redirect('/servers')


@app.route('/swap_up/<int:id>', methods=['POST', 'GET'])
def swap_up(id):
    with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
        j = json.load(f)
    for i in range(len(j['list'])):
        if j['list'][i]['id'] == id and i != 0:
            j['list'][i], j['list'][i - 1] = j['list'][i - 1], j['list'][i]
            break
    with open(os.path.join(sys.path[0], "servers.json"), "w", encoding='UTF-8') as out:
        json.dump(j, out)
    return redirect('/servers')


@app.route('/swap_down/<int:id>', methods=['POST', 'GET'])
def swap_down(id):
    with open(os.path.join(sys.path[0], "servers.json"), "r", encoding='UTF-8') as f:
        j = json.load(f)
    for i in range(len(j['list'])):
        if j['list'][i]['id'] == id and i != len(j['list']) - 1:
            j['list'][i], j['list'][i + 1] = j['list'][i + 1], j['list'][i]
            break
    with open(os.path.join(sys.path[0], "servers.json"), "w", encoding='UTF-8') as out:
        json.dump(j, out)
    return redirect('/servers')


@app.route('/search', methods=['POST'])
def search():
    return redirect('search/{}'.format(request.form['req']))


@app.route('/search/<string:s>')
def searcher(s):
    res = list(map(list, NEWS.get_all(order='date', arg=s)))
    for n in res:
        n[2] = beautiful_tags(n[2])
    print(res)
    if check_admin(session['user_id']):
        return render_template('search_res.html', title='Поиск', res=res, admin='True')
    return render_template('search_res.html', title='Поиск', res=res, admin='False')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
