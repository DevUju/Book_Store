from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Nna123.@localhost:5432/book_store"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Book(db.Model):
    __tablename__ = "Book_List"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    finished = db.Column(db.Boolean, nullable=False)
    checkbox_state = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


@app.route("/")
def index():
    return render_template("index.html", data=Book.query.all())

@app.route("/add/book", methods=["POST"])
def add_book():
    error = False
    try:
        name = request.get_json()["name"]
        newBook = Book(name=name)
        db.session.add(newBook)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if error:
            abort(400)
        else:
            db.session.add(newBook)
            return jsonify(newBook.to_dict())

@app.route("/finished/<int:bookId>/book", methods=['POST'])
def finished_book(bookId):
    try:
        finished = request.get_json["finished"]
        book = Book.query.get(bookId)
        if book is None:
            abort(404)
        book.checkbox_state = finished
        db.session.commit()
        return render_template("index.html", data=Book.query.all(), checkbox_state=finished)
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return "Book update failed"

        
    
    

app.app_context().push()
db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
