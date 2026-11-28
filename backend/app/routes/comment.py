from datetime import UTC, datetime

from flask import Blueprint, request
from flask_security import auth_required, current_user, roles_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Comment, Post

comment_bp = Blueprint("comment", __name__)


@comment_bp.route("/create_comment", methods=["POST"])
@roles_required("member")
@auth_required("token")
def create_comment():
    data = request.json
    content = data.get("content")
    post_id = data.get("post_id")
    parent_id = data.get("parent_id")
    user_id = current_user.id

    try:
        post = db.session.query(Post).filter(Post.id == post_id).first()
        if post is None:
            return "Post doesn't exist", 404

        parent = db.session.query(Comment).filter(Comment.id == parent_id).first()
        if (parent is None) and (parent_id is not None):
            return "Parent comment doesn't exist", 404

        if parent is not None and int(post_id) != int(parent.post_id):
            return "Parent and Child must have the same post", 400

        new_comment = Comment(
            content=content, post_id=post_id, parent_id=parent_id, user_id=user_id
        )
        db.session.add(new_comment)
        db.session.commit()
        return str(new_comment.id), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return str(e), 500


@comment_bp.route("/get_comment/<id>", methods=["GET"])
@auth_required("token")
def get_comment(id):
    db_query = db.session.query(Comment).filter(Comment.id == id)
    db_entry = db_query.first()

    if db_entry is None:
        return "Comment not found.", 404
    else:
        return {
            "id": id,
            "user_id": current_user.id,
            "parent_id": db_entry.parent_id,
            "post_id": db_entry.post_id,
            "content": db_entry.content,
            "children": [
                {
                    "content": i.content,
                    "id": i.id,
                }
                for i in db_entry.children
            ],
            "created_at": db_entry.created_at,
            "modified_at": db_entry.modified_at,
        }


@comment_bp.route("/<user_id>/get_all_comments", methods=["GET"])
@auth_required("token")
def get_all_comment(user_id):
    db_query = db.session.query(Comment).filter(Comment.user_id == user_id)
    posts = db_query.all()

    return [
        {
            "id": i.id,
            "user_id": current_user.id,
            "parent_id": i.parent_id,
            "post_id": i.post_id,
            "content": i.content,
            "created_at": i.created_at,
            "modified_at": i.modified_at,
        }
        for i in posts
    ]


@comment_bp.route("/edit_comment/<id>", methods=["PATCH"])
@roles_required("member")
@auth_required("token")
def edit_comment(id):
    data = request.json
    db_query = db.session.query(Comment).filter(Comment.id == id)
    db_entry = db_query.first()

    if db_entry is None:
        return "Comment not found.", 404
    elif db_entry.user_id != current_user.id:
        return "This comment isn't yours.", 401
    else:
        try:
            content = data.get("content")

            if content:
                db_query.update({"content": content, "modified_at": datetime.now(UTC)})

            db.session.commit()
            return id
        except SQLAlchemyError as e:
            db.session.rollback()
            return str(e), 500


@comment_bp.route("/delete_comment/<id>", methods=["DELETE"])
@auth_required("token")
def delete_comment(id):
    db_query = db.session.query(Comment).filter(Comment.id == id)
    db_entry = db_query.first()

    if db_entry is None:
        return "Comment not found.", 404
    elif (db_entry.user_id != current_user.id) and (not current_user.has_role("admin")):
        return "This comment isn't yours.", 401
    else:
        try:
            db_query.delete()
            db.session.query(Comment).filter(Comment.post_id == id).delete()
            db.session.commit()
            return id
        except SQLAlchemyError as e:
            db.session.rollback()
            return str(e), 500
