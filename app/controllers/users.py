"""Controller to handle user specific operations"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, current_user
from src.utils.error_utils import RequestValidationError, UserNotFound
from app.models import User
from app.schemas import UserSchema
import logging


user_bp = Blueprint("users", __name__)

@user_bp.get("/detail")
@jwt_required()
def get_user_details():
    """Get user details using the JWT token"""
    return jsonify(
        {
            "message": "message",
            "details": {
                "fullname": f"{current_user.firstname} {current_user.lastname}",
                "email": current_user.email,
                "description": current_user.description
            },
        }
    )

@user_bp.put("/update")
@jwt_required()
def update_user_desc():
    """Update user description"""
    data = request.get_json()
    try:
        if "description" not in data:
            raise RequestValidationError("description key is missing")

        user_email = current_user.email
        user_db = User.get_user_by_email(email=user_email)
        if user_db: # check if user exists else raise UserNotFound error
            user_db.description = data.get("description")
            user_db.save()
            return jsonify({"message":"Description updated"}), 200
        raise UserNotFound

    except RequestValidationError as e:
        logging.error(e)
        return jsonify({"error":e.message}), 422
    
    except UserNotFound as e:
        logging.error(e)
        return jsonify({"error":e.message}), 404


@user_bp.delete("/deactivate")
@jwt_required()
def delete_user():
    """ deactivate user by removing the user from DB """
    try:
        user_email = current_user.email # Get the current user from the JWT token
        user_db = User.query.filter_by(email=user_email).first()
        if user_db:
            user_db.delete()
            return jsonify({"message":"User deactivated"}), 200
        raise UserNotFound
    except UserNotFound as e:
        logging.error(e)
        return jsonify({"error":e.message}), 404


@user_bp.get("/limit")
@jwt_required()
def get_limited_users():
    """Get user details in paginated form"""
    claims = get_jwt()
    if claims.get("is_admin") == True:
        page = request.args.get("page", default=1, type=int) # set the page number with default value as 1
        per_page = request.args.get("per_page", default=3, type=int) # set the number of records per page with default value as 3
        users = User.query.paginate(page=page, per_page=per_page)
        result = UserSchema().dump(users, many=True)
        return jsonify({"users": result}), 200
    return jsonify({"message": "You are not authorized to access this"}), 401
