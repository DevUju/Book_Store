from models import Library_User, Author, Book, librarian_book_author
from flask import jsonify, request
from config import app, db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from datetime import timedelta


migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
expiration = timedelta(days=30)


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
        else:
            return jsonify({"status": "Bad request", "message": "Incorrect password", "statusCode": 401}), 401

    except Exception as e:
        return jsonify({
                        "status": "Bad request", 
                        "message": f"Authentication failed {str(e)}", 
                        "statusCode": 401})

# Refresh Token
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) 
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

@app.route("/add/book/library", methods=["POST"])
@jwt_required()
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

        db.session.add(author)
        db.session.add(book)
        db.session.commit()

        if library_user:
            # This particular line of code is attacjing the library_user twice in the association table. I am still trying to figure it out. 
            library_user.book.append(book)
            library_user.author.append(author)
            
            db.session.commit()

            return jsonify({"message": "Book, author, and library user association added successfully"}), 200
        else:
            return jsonify({"message": "Invalid library user"}), 400
    except Exception as e:
        print(f"Error: {str(e)}")  
        return jsonify({"Message": f"Failed to add book, author, and library user association. Error: {str(e)}"}), 400
    

with app.app_context():
    db.create_all()       

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
