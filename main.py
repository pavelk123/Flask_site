from flask import Flask, render_template, url_for, request, redirect, make_response, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = 'ddsf11r13r1'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)

#from main import db
#db.create_all()
#для создания бд (вводить в интерпритатор)
#db.close_all_sessions()

class User(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    #created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    #updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    info = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    parent = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Запись:{self.id} {self.title}, {self.price}, {self.info}'


#admin = User(name='admin',username='admin1',email='sdfsdfsdf@dfsdf',password_hash='123')

@app.route('/registration', methods=['GET', 'POST'])
def registr():
    if request.method == 'POST':
        name = request.form['username']
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        if password == password2:
            isNotInBase = True
            users = User.query.all()
            for user in users:
                if login == user.username:
                    flash('Такой пользователь уже зарегестрирыван',category='danger')
                    isNotInBase = False
                    return redirect(url_for('registr'))
            if isNotInBase is True:
                user_new = User(name=name,username=login,email=email,password_hash=generate_password_hash(password))
                try:
                    db.session.add(user_new)
                    db.session.commit()
                    flash('Вы зарегестрирывались',category='success')
                    return redirect(url_for('registr'))
                except:
                    flash('Что-то пошло не так(((',category='danger')
                    return redirect(url_for('registr'))
        else:
            flash('Пароли не совпадают',category='danger')
            return redirect(url_for('registr'))
    if request.method == 'GET':
        return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        login = request.form['login']
        password= request.form['password']
        user = User.query.filter_by(username=login).first()
        if user is not None:
            if user.username == login and check_password_hash(user.password_hash, password) == True:
                session['userLogged'] = request.form['login']
                flash(f'Вы вошли под ником {session["userLogged"]}',category='primary')
                return redirect(url_for('profile', username=session['userLogged']))
            else:
                flash('Неправильный логин или пароль',category='danger')

        else:
            flash('Такого пользователя не существует', category='danger')
    elif 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
   # elif request.method == 'POST' and request.form['login'] == 'admin' and request.form['password'] == '123':
    #    session['userLogged'] = request.form['login']
    #    flash(f'Вы вошли под ником {session["userLogged"]}')
     #   return redirect(url_for('profile', username=session['userLogged']))


    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))





@app.route('/profile/<username>')
def profile(username):


    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)

    items = Item.query.filter_by(parent=session['userLogged']).all()


    return render_template('profile.html', data=items)


@app.route('/cookie/',)
def cookie():
    res = make_response('Sitting a cookie')
    res.set_cookie('foo', 'bar', max_age=60*60*24*365*2)
    print(url_for('cookie'))
    return res

@app.route('/', )
def index():

    items = Item.query.order_by(Item.price).all()
    print(url_for('index'))
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    print(url_for('about'))
    return render_template('about.html')

@app.route('/rules')
def rules():
    print(url_for('rules'))
    return render_template('rules.html')

@app.route('/create',methods=['POST','GET'])
def create():
    if 'userLogged' not in session:
        abort(401)


    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        info = request.form['info']
        parent = session['userLogged']

        item = Item(title=title,price=price, info=info, parent=parent)
        try:
            db.session.add(item)
            db.session.commit()

            flash('Товар добавлен!',category='success')

            return redirect('/')
        except:
            flash('Что-то пошло не так',category='danger')
            return 'Получилась ошибка'
    else:

        return render_template('create.html')

@app.route('/product/<int:prod_id>', methods=['GET','POST'])
def redact(prod_id):


    if request.method == 'GET':
        try:
            item = Item.query.get(prod_id)
            if 'userLogged' not in session or item.parent != session['userLogged']:
                abort(401)

            return render_template('redact.html',item=item)
        except:
            return 'Произошла ошибка'

    if request.method == 'POST':
        item = Item.query.get(prod_id)

        title = request.form['title']
        price = request.form['price']
        info = request.form['info']

        item.title = title
        item.price = price
        item.info = info

        db.session.commit()
        flash('Товар изменен', category='primary')
        return redirect('/')

@app.route('/delete/<prod_id>',methods=['GET','POST'])
def delete(prod_id):

    if request.method == 'GET':

        try:
            item = Item.query.get(prod_id)
            if 'userLogged' not in session or item.parent != session['userLogged']:
                abort(401)

            return render_template('delete.html',item=item)
        except:

            flash('Произошла ошибка')
    if request.method == 'POST':
        item = Item.query.get(prod_id)
        db.session.delete(item)
        db.session.commit()
        flash('Товар удален!', category='danger')
        return redirect('/')

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html'), 404



#тестирование
#with app.test_request_context():
#    print(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)