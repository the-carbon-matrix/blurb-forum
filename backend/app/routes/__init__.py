from flask import Blueprint
from flask_security import auth_required, current_user

from .admin import admin_bp
from .post import post_bp
from .comment import comment_bp

main = Blueprint("main", __name__, url_prefix="/api")
main.register_blueprint(admin_bp, url_prefix="/admin")
main.register_blueprint(post_bp, url_prefix="/post")
main.register_blueprint(comment_bp, url_prefix="/comment")


@main.route("/profile", methods=["GET"])
@auth_required("token")
def get_profile():
    return {
        "username": current_user.username,
        "email": current_user.email,
        "id": current_user.id,
        "is_active": current_user.is_active,
        "created_at": current_user.create_datetime,
        "roles": [role.name for role in current_user.roles],
    }
