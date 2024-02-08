from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String

db = SQLAlchemy()

Table = db.Table
relationship = db.relationship


class Model(db.Model):
    __abstract__ = True

    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<{self.__class__.__name__} ({self.created_at})>'

    def serialize(self) -> dict:
        return vars(self)


class Entity(Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    description = Column(String(512))

    def __repr__(self):
        return f'<{self.__class__.__name__} (id={self.id} name=\'{self.name}\')>'
