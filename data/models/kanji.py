import sqlalchemy
from data.db_session import SqlAlchemyBase


class Kanji(SqlAlchemyBase):
    __tablename__ = 'kanji'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False, index=True)
    onyomi_reading = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    kunyomi_reading = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    meaning = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    examples = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    path_to_sound = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    path_to_image = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
