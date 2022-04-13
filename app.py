from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
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


@app.route("/")
def home():
    book_details = Book.query.all()
    return render_template("data.html", book_details=book_details,book=Book)


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


@app.route("/delete/<int:book_id>")
def delete(book_id):
    book = Book.query.filter_by(id=book_id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home"))


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
