from datetime import UTC, datetime

from flask_security.models import fsqla_v4 as fsqla
from sqlalchemy import ForeignKey, Integer, String
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


class Post(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    modified_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))

    # User ID being null means the original user got deleted
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    user: Mapped["User | None"] = relationship("User", back_populates="posts")

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"), nullable=True)

    parent: Mapped["Post | None"] = relationship(
        "Post", remote_side="Post.id", back_populates="children"
    )

    children: Mapped[list["Post"]] = relationship("Post", back_populates="parent")
