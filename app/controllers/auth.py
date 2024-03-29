"""Controller to handle user authenticatio (signup, login, logout)"""
from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    current_user,
    get_jwt_identity,
)
from marshmallow import ValidationError
from app.models import User, TokenBlocklist
from app.schemas import RegistrationSchema
from random import randint
from src.utils.email_utils import EmailUtils
from datetime import datetime
import logging


auth_bp = Blueprint("auth", __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

email_util = EmailUtils()

def schema_error_parser(err_obj):
    """Function to parse the schema validation error details"""
    err_array = [f"{key}: {err[0]}" for key,err in err_obj.items()]
    schema_error = ' & '.join(err_array)
    return schema_error


@auth_bp.post("/signup")
def register_user():
    """
    Handler function for user registration
    returns a success message
    """
    data = request.get_json()
    logger.info("[REGISTER REQUEST BODY]: %s", data)
    schema = RegistrationSchema()
    try:
        schema.load(data) # Validate the request body with the Schema
    except ValidationError as e:
        logging.error("Request validation failed, %s",e)
        return jsonify ({"error": schema_error_parser(e.messages)}), 422

    user_email = User.get_user_by_email(email=data.get("email"))

    if user_email is not None:
        logging.error("User already exists!!!")
        return jsonify({"error": f"User with email - '{user_email.email}' already exists. Please login"}),409

    new_user = User(
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
        description = data.get("description",None),
        email=data.get("email")
        )
    new_user.set_password(password=data.get("password"))
    new_user.save()
    return jsonify({"message": "User created"}), 201



@auth_bp.post("/login")
def login_user():
    """
    desc: Handler function for user login
    returns: Pair of JWT access token and refrest token
    """
    data = request.get_json()
    user_email = data.get("email")
    password = data.get("password")

    user = User.get_user_by_email(email=user_email)

    if user and (user.check_password(password=password)): # Check if the user a registered user and that the password is correct
        otp = str(randint(100000, 999999))
        session[user_email] = otp # Store the OTP in the flask session for later retrieval during verification
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%m-%Y %H:%M")
        email_payload = {
            "recipient_email": user_email,
            "subject": f"OTP RECEIVED FOR LOGIN AT {formatted_datetime}",
            "body": f"Please find your OTP: {otp}"
        }
        email_util.send_email(payload=email_payload) # send email to the user with the payload holding the email contents
        return (
            jsonify(
                {
                    "message": "An OTP is sent over your registered email. Please check and verify!"
                }
            ),
            200,
        )

    return jsonify({"error": "Invalid username or password"}), 400


@auth_bp.post("/verify-otp")
def verify_otp():
    """
    desc: Handler function for user otp verification
    returns: Pair of JWT access and refresh tokens once the otp is validated successfully
    """
    data = request.get_json()
    user_otp = data.get("otp")
    user_email = data.get("email")
    stored_otp = session.get(user_email) # Get the stored OTP that was saved during login
    if stored_otp and user_otp == stored_otp:
        access_token = create_access_token(identity=user_email)
        refresh_token = create_refresh_token(identity=user_email)
        # OTP verification successful
        session.pop(user_email)  # Remove OTP from session after successful verification
        return (
            jsonify(
                {
                    "message": "Success Logged In",
                    "tokens": {"access": access_token, "refresh": refresh_token},
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "Invalid OTP"}), 400

@auth_bp.get("/refresh")
@jwt_required(refresh=True)
def refresh_access():
    """
    Handler function to get a access token using refresh token provided by client side
    returns a access token
    """
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token})

@auth_bp.get('/logout')
@jwt_required(verify_type=False) 
def logout_user():
    """
    Handler to perform user logout by registering the access token id to the blocked list in DB
    return a success message indicating user got logged out
    """
    jwt = get_jwt()
    jti = jwt['jti']
    token_type = jwt['type']
    token_b = TokenBlocklist(jti=jti) # Register the access token to the blocked list
    token_b.save()
    return jsonify({"message": f"{token_type} token revoked successfully"}) , 200

