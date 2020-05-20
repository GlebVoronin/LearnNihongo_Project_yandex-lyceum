import sqlalchemy
from data.db_session import SqlAlchemyBase


class Word(SqlAlchemyBase):
    __tablename__ = 'word'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    reading = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    meaning = sqlalchemy.Column(sqlalchemy.String, nullable=False, index=True)
    way_to_sound = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
    way_to_image = sqlalchemy.Column(sqlalchemy.String, nullable=True, index=True)
