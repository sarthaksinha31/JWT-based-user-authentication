from src.utils.extension_utils import db
import uuid
import bcrypt
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    firstname = db.Column(db.String(), nullable=False)
    lastname = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.Text())

    def __repr__(self):
        return f"{self.id} {self.firstname} {self.lastname} {self.email} {self.description}"

    def set_password(self, password):
        """Hashing password with salt"""
        self.password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

    def check_password(self, password):
        """Verifying password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    @classmethod
    def get_user_by_email(cls, email):
        """Get user details using email"""
        return cls.query.filter_by(email=email).first()

    def save(self):
        """Save user information in the DB"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete a user in the DB"""
        db.session.delete(self)
        db.session.commit()


class TokenBlocklist(db.Model):
    """DB Model to register a token in the block list"""
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=True)
    create_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti} {self.create_at}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()