from src.dms.exceptions.base import Error


class DAOError(Error):
    pass


class ModelDAOError(DAOError):
    pass


class EntityDAOError(ModelDAOError):
    pass
