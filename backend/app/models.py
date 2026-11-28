from datetime import UTC, datetime

from flask_security.models import fsqla_v4 as fsqla
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db

fsqla.FsModels.set_db_info(db)  # pyright: ignore[reportPrivateImportUsage]


class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__ = "role"


class FsRefreshTracker(db.Model, fsqla.FsRefreshTrackerMixin):
    __tablename__ = "refresh_tracker"


class User(db.Model, fsqla.FsUserMixin):
    __tablename__ = "user"
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")


utc_now = lambda: datetime.now(UTC)


class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped["User | None"] = relationship("User", back_populates="posts")

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped["User | None"] = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id"), nullable=True
    )
    parent: Mapped["Comment | None"] = relationship(
        "Comment", remote_side="Comment.id", back_populates="children"
    )
    children: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent")
