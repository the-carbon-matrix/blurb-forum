from flask import Blueprint, g
from flask_security import auth_required

main = Blueprint("main", __name__, url_prefix="/api")


@main.route("/", methods=["GET"])
@auth_required("token")
def test():
    return f"Hi! {getattr(g, 'fs_authn_via', None)}"
