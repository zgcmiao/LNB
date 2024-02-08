import logging
from typing import Optional, TypeVar, Generic, List, Type, Iterable, Tuple, Dict, Any

from sqlalchemy import Column, ColumnExpressionArgument, func
from sqlalchemy.orm import load_only

from src.dms.exceptions.dao import ModelDAOError, EntityDAOError
from src.dms.models import db, Model, Entity

_T_MODEL = TypeVar('_T_MODEL', bound=Model)
_T_ENTITY = TypeVar('_T_ENTITY', bound=Entity)

logger = logging.getLogger(__name__)


class ModelDAO(Generic[_T_MODEL]):
    __model_class__: Type[Model] = None

    @classmethod
    def get_model_class(cls) -> Type[_T_MODEL]:
        model_class = cls.__model_class__
        if model_class is None:
            cls_name = cls.__name__
            raise ModelDAOError('model class not specified',
                                f'Please define model class as `__model_class__` in {cls_name}')
        return model_class

    @classmethod
    def get_list(cls,
                 filters: List[ColumnExpressionArgument[bool]] = None,
                 order_by: Column | Tuple = None,
                 offset: int = None,
                 limit: int = None) -> Iterable[_T_MODEL]:
        model_class = cls.get_model_class()
        query = model_class.query
        if filters:
            query = query.filter(*filters)
        if order_by:
            query = query.order_by(order_by)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query

    @classmethod
    def count(cls,
              filters: List[ColumnExpressionArgument[bool]] = None) -> int:
        model_class = cls.get_model_class()
        if hasattr(model_class, 'id'):
            query = db.session.query(func.count(model_class.id))
            if filters:
                query = query.filter(*filters)
            query = query.scalar()
        else:
            query = db.session.query(model_class)
            if filters:
                query = query.filter(*filters)
            logger.warning(f'counting on sub-query: {query}')
            query = query.count()
        return query

    @classmethod
    def search(cls,
               key: str,
               columns: List[Column],
               case_sensitive: bool = False,
               **kwargs) -> Iterable[_T_MODEL]:
        key = key.strip()
        if not key:
            return []
        if case_sensitive:
            filters = [c.like(f'%{key}%') for c in columns]
        else:
            filters = [c.ilike(f'%{key}%') for c in columns]
        return cls.get_list(filters, **kwargs)

    @classmethod
    def add(cls, **kwargs) -> _T_MODEL:
        model_class = cls.get_model_class()
        cls.check_fields(kwargs)
        model_instance = model_class(**kwargs)
        db.session.add(model_instance)
        db.session.commit()
        return model_instance

    @classmethod
    def add_all(cls, kwargs_list: List[Dict]) -> List[_T_MODEL]:
        model_class = cls.get_model_class()
        all_instances = []
        for kwargs in kwargs_list:
            model_instance = model_class(**kwargs)
            all_instances.append(model_instance)
        db.session.add_all(all_instances)
        db.session.commit()
        return all_instances

    @classmethod
    def update(cls, model: _T_MODEL, **kwargs):
        cls.check_fields(kwargs, model)
        for k, v in kwargs.items():
            setattr(model, k, v)

    @classmethod
    def update_by_filter_by(cls, filters, update_data):
        model_class = cls.get_model_class()
        query = model_class.query
        query.filter_by(**filters).update(update_data)
        db.session.commit()

    @classmethod
    def update_by_filter(cls, filters: List[ColumnExpressionArgument[bool]], update_data: dict):
        model_class = cls.get_model_class()
        query = model_class.query
        query.filter(*filters).update(update_data)
        db.session.commit()

    @classmethod
    def check_fields(cls, fields: Dict[str, Any], model: _T_MODEL = None):
        pass

    @staticmethod
    def remove(obj: _T_MODEL):
        db.session.remove(obj)

    @classmethod
    def remove_all(cls):
        db.session.query(cls.get_model_class()).delete()


class EntityDAO(ModelDAO[_T_MODEL]):
    @classmethod
    def get_by_id(cls, _id: int) -> Optional[_T_ENTITY]:
        if _id is None:
            raise EntityDAOError('id is required')
        if type(_id) is not int:
            raise EntityDAOError('id must be an integer')

        return cls.get_model_class().query.get(_id)

    @classmethod
    def get_by_name(cls, name: str) -> Optional[_T_ENTITY]:
        if not name:
            raise EntityDAOError('name is required')

        return cls.get_model_class().query.filter_by(name=name).first()
