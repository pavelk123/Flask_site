from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'sqlite:///shop.db'
db = SQLAlchemy(app)

#from main import db
#db.create_all()
#для создания бд (вводить в интерпритатор)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    info = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'Запись: {self.title}, {self.price}, {self.info}'

@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/rules')
def rules():
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
            return redirect('/')
        except:
            return 'Получилась ошибка'
    else:

        return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True)