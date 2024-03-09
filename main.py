from flask import Flask, jsonify
from src.utils.extension_utils import db, jwt
from src.constants import ADMIN_EMAIL
from app.controllers.auth import auth_bp
from app.controllers.users import user_bp
from app.models import User, TokenBlocklist

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env() # Set the environment variables for the flask application

    # initialize extentions
    db.init_app(app)
    jwt.init_app(app)

    # register bluepints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")

    # load user
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        """Get the subject claim which is holding the user identity"""
        identity = jwt_data["sub"]
        return User.query.filter_by(email=identity).one_or_none()

    # additional claims
    @jwt.additional_claims_loader
    def make_additional_claims(identity):
        """Add a JWT claim with field as is_admin to identify if the user is admin or not"""
        if identity == ADMIN_EMAIL:
            return {"is_admin": True}
        return {"is_admin": False}

    # jwt error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        """Returns status code as 401 if the token has expired"""
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Returns status code as 401 if the token signature validation fails"""
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Returns status code as 401 if the token is not valid"""
        return (
            jsonify(
                {
                    "message": "Request doesnt contain valid token",
                    "error": "authorization_header",
                }
            ),
            401,
        )
    
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header,jwt_data):
        """Check if the token id is in the DB blocked list or not"""
        jti = jwt_data['jti']
        token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()
        return token is not None

    return app
