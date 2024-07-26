from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import current_app
import sys

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Nna123.@localhost:5432/book_store"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

book_author = db.Table(
    "book_author",
    db.Column("book_id", db.Integer, db.ForeignKey("Book_List.id")),
    db.Column("author_id", db.ForeignKey("author.id"))
)

class Author(db.Model):
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Author's Details: {self.id}. {self.first_name} {self.last_name}"

class Book(db.Model):
    __tablename__ = "Book_List"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    finished = db.Column(db.Boolean, default=False)
    author = db.relationship("Author", secondary="book_author", backref=db.backref('books', lazy=True))
    def __repr__(self):
        return f"Book's Details: {self.id}. {self.name} {self.author}"

def add_book():
    author1_first_name = input("Enter first name of author 1: ")
    author1_last_name = input("Enter last name of author 1: ")
    author2_first_name = input("Enter first name of author 2: ")
    author2_last_name = input("Enter last name of author 2: ")
    author3_first_name = input("Enter first name of author 3: ")
    author3_last_name = input("Enter last name of author 3: ")

    book1_name = input("Enter title of book 1: ")
    book2_name = input("Enter title of book 2: ")
    book3_name = input("Enter title of book 3: ")

    author1 = Author(first_name=author1_first_name, last_name=author1_last_name)
    author2 = Author(first_name=author2_first_name, last_name=author2_last_name)
    author3 = Author(first_name=author3_first_name, last_name=author3_last_name)
    book1 = Book(name=book1_name)
    book2 = Book(name=book2_name)
    book3 = Book(name=book3_name)

    book1.author.append(author1)
    book1.author.append(author2)
    book1.author.append(author3)
    book2.author.append(author1)
    book2.author.append(author2)
    book2.author.append(author3)
    book3.author.append(author1)
    book3.author.append(author2)
    book3.author.append(author3)

    
    db.session.add_all([book1, book2, book3])
    db.session.commit()

# @app.route("/")
# def index():
#     return render_template("index.html", data=Book.query.all())

# @app.route("/add/book", methods=["POST"])
# def add_book():
#     error = False
#     try:
#         name = request.get_json()["name"]
#         newBook = Book(name=name)
#         db.session.add(newBook)
#         db.session.commit()
#     except:
#         error = True
#         db.session.rollback()
#         print(sys.exc_info())
#     finally:
#         if error:
#             abort(400)
#         else:
#             db.session.add(newBook)
#             return jsonify(newBook.to_dict())

# @app.route("/finished/<int:bookId>/book", methods=['POST'])
# def finished_book(bookId):
#     try:
#         finished = request.get_json["finished"]
#         book = Book.query.get(bookId)
#         if book is None:
#             abort(404)
#         db.session.commit()
#         return redirect(url_for("index", checkbox_state=finished))
#     except:
#         db.session.rollback()
#     finally:
#         db.session.close()
#     return "Book update failed"

        
    
    

with app.app_context():
    add_book()
    db.create_all()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=4000)
