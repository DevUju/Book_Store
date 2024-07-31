from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from dotenv import load_dotenv
import secrets
import os

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
expiration = timedelta(minutes=60.0)

if not os.path.isfile('secret_key.txt'):
    secret_key = secrets.token_urlsafe(32)
    with open('secret_key.txt', 'w') as f:
        f.write(secret_key)
else:
    with open('secret_key.txt', 'r') as f:
        secret_key = f.read()

app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = secret_key
app.config['JWT_TOKEN_LOCATION'] = ['headers']

# Validate Model
def validate_model(model):
    try:
        db.session.add(model)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        errors = []
        for err in e.orig.args:
            errors.append({"field": err.split()[0], "message": " ".join(err.split()[1:])})
        return jsonify({"errors": errors}), 422
    return  jsonify({"message": "User created successfully!"}), 201

# Create a Librarian Model
class Librarian(db.Model):
    __tablename__ = "librarian_table"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"iD: {self.id}. Name: {self.first_name} {self.last_name}"

#Implement User Registration
@app.route("/user/register", methods=["PoST"])
def user_register():
    try:
        data = request.get_json()
        u_name = data["username"]
        f_name = data["first_name"]
        l_name = data["last_name"]
        user_email = data["email"]
        user_password = data["password"]

        hashed_password = bcrypt.generate_password_hash(user_password).decode("utf-8")

        library_user = Librarian(
            username = u_name,
            first_name = f_name,
            last_name = l_name,
            email = user_email,
            password = hashed_password
        )

        validate_model(library_user)

        db.session.add(library_user)
        db.session.commit()

        return jsonify({
            "Status": "Success",
            "Message": "Registration Successful",
                "librarian": {
                    "id": library_user.id,
                    "username": library_user.username,
                    "first_name": library_user.first_name,
                    "last_name": library_user.last_name,
                    "email": library_user.email
                }
            }
        ), 200
    except:
        return jsonify({
                        "status": "Bad request", 
                        "message": "Registration failed", 
                        "statusCode": 401})

#Implement User Login and Authentication
@app.route("/user/login", methods=["POST"])
def user_login():
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        user = Librarian.query.filter_by(username=username).first()

        if user is None:
            return jsonify({"status": "Bad request", "message": "User not found", "statusCode": 404}), 404
        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=username, expires_delta=expiration)
            return jsonify({
                "Status": "Success",
                "Message": "Login Successful",
                "data": {
                    "Access_Token": access_token,
                    "librarian": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email
                    }

                }
            }), 200
    except:
        return jsonify({
                        "status": "Bad request", 
                        "message": "Authentication failed", 
                        "statusCode": 401})
                    


# book_author = db.Table(
#     "book_author",
#     db.Column("book_id", db.Integer, db.ForeignKey("Book_List.id")),
#     db.Column("author_id", db.ForeignKey("author.id"))
# )

# class Author(db.Model):
#     __tablename__ = "author"
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(), nullable=False)
#     last_name = db.Column(db.String(), nullable=False)

#     def __repr__(self):
#         return f"Author's Details: {self.id}. {self.first_name} {self.last_name}"

# class Book(db.Model):
#     __tablename__ = "Book_List"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(), nullable=False, unique=True)
#     finished = db.Column(db.Boolean, default=False)
#     author = db.relationship("Author", secondary="book_author", backref=db.backref('books', lazy=True))
#     def __repr__(self):
#         return f"Book's Details: {self.id}. {self.name} {self.author}"

# def add_book():
#     author1_first_name = input("Enter first name of author 1: ")
#     author1_last_name = input("Enter last name of author 1: ")
#     author2_first_name = input("Enter first name of author 2: ")
#     author2_last_name = input("Enter last name of author 2: ")
#     author3_first_name = input("Enter first name of author 3: ")
#     author3_last_name = input("Enter last name of author 3: ")

#     book1_name = input("Enter title of book 1: ")
#     book2_name = input("Enter title of book 2: ")
#     book3_name = input("Enter title of book 3: ")

#     author1 = Author(first_name=author1_first_name, last_name=author1_last_name)
#     author2 = Author(first_name=author2_first_name, last_name=author2_last_name)
#     author3 = Author(first_name=author3_first_name, last_name=author3_last_name)
#     book1 = Book(name=book1_name)
#     book2 = Book(name=book2_name)
#     book3 = Book(name=book3_name)

#     book1.author.append(author1)
#     book1.author.append(author2)
#     book1.author.append(author3)
#     book2.author.append(author1)
#     book2.author.append(author2)
#     book2.author.append(author3)
#     book3.author.append(author1)
#     book3.author.append(author2)
#     book3.author.append(author3)

    
#     db.session.add_all([book1, book2, book3])
#     db.session.commit()

with app.app_context():
    # add_book()
    db.create_all()

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

        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
