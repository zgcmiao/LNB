from enum import Enum


class BaseEnum(Enum):
    def __str__(self):
        return self.value


def model_to_dict(model_obj):
    d = {}
    for column in model_obj.__table__.columns:
        d[column.name] = str(getattr(model_obj, column.name))

    return d
