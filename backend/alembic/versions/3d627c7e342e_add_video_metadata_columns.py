"""add_video_metadata_columns

Revision ID: 3d627c7e342e
Revises: 0001
Create Date: 2026-07-25 01:32:54.999896
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d627c7e342e"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "uploads",
        sa.Column("duration", sa.Float(), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("width", sa.Integer(), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("height", sa.Integer(), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("fps", sa.Float(), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("codec", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("bitrate", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("container_format", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("thumbnail_path", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("uploads", "thumbnail_path")
    op.drop_column("uploads", "container_format")
    op.drop_column("uploads", "bitrate")
    op.drop_column("uploads", "codec")
    op.drop_column("uploads", "fps")
    op.drop_column("uploads", "height")
    op.drop_column("uploads", "width")
    op.drop_column("uploads", "duration")