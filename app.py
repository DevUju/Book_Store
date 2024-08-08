from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from dotenv import load_dotenv
import secrets
import os
import datetime

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
expiration = timedelta(days=30)

secret_key = os.getenv("SECRET_KEY")

app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = secret_key
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = expiration


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

# Create librarian_book_author Association Table
librarian_book_author = db.Table(
    "library",
    db.Column("library_user_id", db.Integer, db.ForeignKey("library_user_table.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("book_table.id")),
    db.Column("author_id", db.Integer, db.ForeignKey("author_table.id"))
)

# Create a Librarian Model
class Library_User(db.Model):
    __tablename__ = "library_user_table"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    book = db.relationship("Book", secondary="librarian_book_author", backref=db.backref('library_user', lazy=True))
    author = db.relationship("Author", secondary="librarian_book_author", backref=db.backref('library_user', lazy=True))

    def __repr__(self):
        return f"iD: {self.id}. Name: {self.first_name} {self.last_name}"
    
# Create Book Model
class Book(db.Model):
    __tablename__ = "book_table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow())
    
    def __repr__(self):
        return f"Book's Details: {self.id}. {self.name}"

# Create Author Model
class Author(db.Model):
    __tablename__ = "author_table"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Author's Details: {self.id}. {self.first_name} {self.last_name}"


#Implement User Registration
@app.route("/user/register", methods=["POST"])
def user_register():
    try:
        data = request.get_json()
        u_name = data["username"]
        f_name = data["first_name"]
        l_name = data["last_name"]
        user_email = data["email"]
        user_password = data["password"]
        
        # Check if username or email already exists
        existing_user = Library_User.query.filter((Library_User.username == u_name) | (Library_User.email == user_email)).first()
        if existing_user:
            return jsonify({
                "message": "Username or email already exists", 
                "status": "Bad request", 
                "statusCode": 401})


        hashed_password = bcrypt.generate_password_hash(user_password).decode("utf-8")

        library_user = Library_User(
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
        user = Library_User.query.filter_by(username=username).first()

        if user is None:
            return jsonify({"status": "Bad request", "message": "User not found", "statusCode": 404}), 404
        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=username, expires_delta=expiration)
            refresh_token = create_refresh_token(identity=username)
            return jsonify({
                "Status": "Success",
                "Message": "Login Successful",
                "data": {
                    "Access_Token": access_token,
                    "Refresh_Token": refresh_token,
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

# Refresh Token
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token), 200

@app.route("/add/book/library", methods=["POST"])
@jwt_required(refresh=True)
def add_book():
    try:
        data = request.get_json()
        book_name = data["name"]
        author_first_name = data["first_name"]
        author_last_name = data["last_name"]
        library_user_id = data["id"]

        author = Author(first_name=author_first_name, last_name=author_last_name)
        book = Book(name=book_name)
        library_user = Library_User.query.get(library_user_id)

        if library_user:
            library_user.book.append(book)
            library_user.author.append(author)
            db.session.add_all([author, book, library_user])
            db.session.commit()

            return jsonify({"message": "Book, author, and library user association added successfully"}), 200
        else:
            return jsonify({"message": "Invalid library user"}), 400
    except:
        return jsonify({"message": "Failed to add book, author, and library user association"}), 400



                    
with app.app_context():
    db.create_all()       

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
