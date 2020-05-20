import sqlalchemy
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    hiragana_save = sqlalchemy.Column(sqlalchemy.Integer, default=1, index=True)
    katakana_save = sqlalchemy.Column(sqlalchemy.Integer, default=1, index=True)
    kanji_save = sqlalchemy.Column(sqlalchemy.Integer, default=1, index=True)
    words_save = sqlalchemy.Column(sqlalchemy.Integer, default=1, index=True)
