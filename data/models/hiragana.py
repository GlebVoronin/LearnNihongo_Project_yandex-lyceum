import sqlalchemy
from data.db_session import SqlAlchemyBase


class Hiragana(SqlAlchemyBase):
    __tablename__ = 'hiragana'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False, index=True)
    reading = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    path_to_sound = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
