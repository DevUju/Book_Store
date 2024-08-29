from config import db
import datetime

# Create librarian_book_author Association Table
librarian_book_author = db.Table(
    "librarian_book_author",  
    db.Column("library_user_id", db.Integer, db.ForeignKey("library_user_table.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("book_table.id")),
    db.Column("author_id", db.Integer, db.ForeignKey("author_table.id"))
)

# Create a Library_User Model
class Library_User(db.Model):
    __tablename__ = "library_user_table"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False, unique=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)

    books = db.relationship("Book", secondary="librarian_book_author", backref=db.backref('library_users', lazy=True))
    authors = db.relationship("Author", secondary="librarian_book_author", backref=db.backref('library_users', lazy=True))

    def __repr__(self):
        return f"ID: {self.id}. Name: {self.first_name} {self.last_name}"
    
# Create Book Model
class Book(db.Model):
    __tablename__ = "book_table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.datetime.utcnow())
    
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