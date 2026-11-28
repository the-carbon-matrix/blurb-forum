from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, request
from flask_security import auth_required, current_user, roles_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Comment, Post

post_bp = Blueprint("post", __name__)


@post_bp.route("/create_post", methods=["POST"])
@roles_required("member")
@auth_required("token")
def create_post():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    user_id = current_user.id

    try:
        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return str(new_post.id), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return str(e), 500


@post_bp.route("/get_post/<id>", methods=["GET"])
@auth_required("token")
def get_post(id):
    db_query = db.session.query(Post).filter(Post.id == id)
    db_entry = db_query.first()

    if db_entry is None:
        return "Post not found.", 404
    else:
        return {
            "id": id,
            "user_id": current_user.id,
            "title": db_entry.title,
            "content": db_entry.content,
            "children": [
                {
                    "content": i.content,
                    "id": i.id,
                }
                for i in db_entry.comments
                if i.parent_id == None
            ],
            "created_at": db_entry.created_at,
            "modified_at": db_entry.modified_at,
        }


@post_bp.route("/get_today_posts", methods=["GET"])
@auth_required("token")
def get_today_posts():
    tz_arg = request.args.get("tz")
    tz = ZoneInfo(tz_arg) if tz_arg else ZoneInfo("UTC")

    local_now = datetime.now(tz)

    local_start = datetime.combine(local_now.date(), time.min, tzinfo=tz)
    local_end = local_start + timedelta(days=1)

    utc_start = local_start.astimezone(UTC)
    utc_end = local_end.astimezone(UTC)

    posts = db.session.query(Post).filter(
        Post.created_at >= utc_start,
        Post.created_at < utc_end,
    )

    return [
        {
            "id": i.id,
            "user_id": current_user.id,
            "title": i.title,
            "content": i.content,
            "children": [
                {
                    "content": j.content,
                    "id": j.id,
                }
                for j in i.comments
                if j.parent_id == None
            ],
            "created_at": i.created_at,
            "modified_at": i.modified_at,
        }
        for i in posts
    ]


@post_bp.route("/<user_id>/get_all_posts", methods=["GET"])
@auth_required("token")
def get_all_posts(user_id):
    db_query = db.session.query(Post).filter(Post.user_id == user_id)
    db_entry = db_query.first()
    if db_entry is None:
        return "Post not found.", 404
    posts = db_query.all()

    return [
        {
            "id": i.id,
            "user_id": current_user.id,
            "title": i.title,
            "content": i.content,
            "children": [
                {
                    "content": j.content,
                    "id": j.id,
                }
                for j in i.comments
                if j.parent_id == None
            ],
            "created_at": i.created_at,
            "modified_at": i.modified_at,
        }
        for i in posts
    ]


@post_bp.route("/edit_post/<id>", methods=["PATCH"])
@roles_required("member")
@auth_required("token")
def edit_post(id):
    data = request.json
    db_query = db.session.query(Post).filter(Post.id == id)
    db_entry = db_query.first()

    if db_entry is None:
        return "Post not found.", 404
    elif db_entry.user_id != current_user.id:
        return "This post isn't yours.", 401
    else:
        try:
            title = data.get("title")
            content = data.get("content")

            if title:
                db_query.update({"title": title, "modified_at": datetime.now(UTC)})

            if content:
                db_query.update({"content": content, "modified_at": datetime.now(UTC)})

            db.session.commit()
            return id
        except SQLAlchemyError as e:
            db.session.rollback()
            return str(e), 500


@post_bp.route("/delete_post/<id>", methods=["DELETE"])
@auth_required("token")
def delete_post(id):
    db_query = db.session.query(Post).filter(Post.id == id)
    db_entry = db_query.first()

    if db_entry is None:
        return "Post not found.", 404
    elif (db_entry.user_id != current_user.id) and (not current_user.has_role("admin")):
        return "This post isn't yours.", 401
    else:
        try:
            db_query.delete()
            db.session.query(Comment).filter(Comment.post_id == id).delete()
            db.session.commit()
            return id
        except SQLAlchemyError as e:
            db.session.rollback()
            return str(e), 500
