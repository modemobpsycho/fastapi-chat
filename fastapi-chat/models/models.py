from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

metadata = MetaData()

roles = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("password", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.now(datetime.UTC)),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)
