from flask import Flask, render_template, url_for, request, redirect, make_response, flash, session
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

    def __repr__(self):
        return f'Запись: {self.title}, {self.price}, {self.info}'



@app.route('/login', methods=['GET','POST'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['login'] == 'admin' and request.form['password'] == '123':
        session['userLogged'] = request.form['login']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html')


@app.route('/profile/<username>')
def profile(username):
    return "Пользователь"+username


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
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        info = request.form['info']

        item = Item(title=title,price=price, info=info)
        try:
            db.session.add(item)
            db.session.commit()

            flash('Товар добавлен!',category='success')

            return redirect('/')
        except:
            return 'Получилась ошибка'
    else:

        return render_template('create.html')

@app.route('/product/<int:prod_id>', methods=['GET','POST'])
def redact(prod_id):

    if request.method == 'GET':
        try:
            item = Item.query.get(prod_id)
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
            return render_template('delete.html',item=item)
        except:

            return 'Произошла ошибка'
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