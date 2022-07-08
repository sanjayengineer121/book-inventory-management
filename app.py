from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql.expression import select, exists
import hashlib

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmanage.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(200))
    complete = db.Column(db.Boolean)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'complete': self.complete
        }
    def __repr__(self) -> str:
        return f'{self.id} - {self.title}'

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(30))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'complete': self.complete
        }
    def __repr__(self) -> str:
        return f'{self.id} - {self.title}'

class admint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(30))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'complete': self.complete
        }
    def __repr__(self) -> str:
        return f'{self.id} - {self.title}'

import os.path
file_exists = os.path.exists('bookmanage.sqlite')
if file_exists==1:
    pass
else:
    db.create_all()


@app.route("/",methods = ['POST', 'GET'])
def demo():
    book_details = Book.query.all()
    return render_template("login.html", book_details=book_details,book=Book)

@app.route("/books")
def home():
    book_details = Book.query.all()
    return render_template("data1.html", book_details=book_details,book=Book)

@app.route("/book")
def home1():
    book_details = Book.query.all()
    return render_template("data.html", book_details=book_details,book=Book)

@app.route("/login", methods=["POST"])
def logi():
    Username= request.form.get("Username")
    password = request.form.get("password")
    print(Username)
    print(password)

    engine = create_engine('sqlite:///bookmanage.sqlite')
    Session = sessionmaker(bind=engine)
    import sqlalchemy
    
    session = Session()
    hash1 = hashlib.md5(password.encode("utf-8")).hexdigest()

    s1=session.query(exists().where(admint.username==Username,admint.password==hash1)).scalar()
    s2=session.query(exists().where(Login.username==Username,Login.password==hash1)).scalar()

    if s1==1:
        book_details = Book.query.all()
        return render_template("data.html", book_details=book_details,book=Book)

    elif s2==1:
        book_details = Book.query.all()
        return render_template("data1.html", book_details=book_details,book=Book)

@app.route("/signup", methods = ['POST', 'GET'])
def singup():

    return render_template('signup.html')

@app.route("/adddata", methods=["POST"])
def adduser():
    

    Username= request.form.get("Username")
    password = request.form.get("password")
    password2 = request.form.get("password1")
    print(Username)
    print(password)

    if password==password2:
        hash1 = hashlib.md5(password.encode("utf-8")).hexdigest()

        sale=Login(username=Username,password=hash1)
        db.session.add(sale)
        db.session.commit()

        print("successfully Addes")
        return redirect(url_for("demo"))
    else:
        return "password Not Matched kindly Try Again"


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    author = request.form.get("author")
    newdata = Book(title=title,author=author, complete=False)
    db.session.add(newdata)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:book_id>")
def update(book_id):
    book = Book.query.filter_by(id=book_id).first()
    book.complete = not book.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update1/<int:book_id>")
def update1(book_id):
    book = Book.query.filter_by(id=book_id).first()
    book.complete = not book.complete
    db.session.commit()
    return redirect(url_for("home1"))


@app.route("/delete/<int:book_id>")
def delete(book_id):
    book = Book.query.filter_by(id=book_id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home1"))


@app.route('/api/data')
def data():
    query = Book.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Book.id.like(f'%{search}%'),
            Book.title.like(f'%{search}%'),
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['id', 'title']:
            col_name = 'title'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Book, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [book.to_dict() for book in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Book.query.count(),
        'draw': request.args.get('draw', type=int),
    }
   

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
