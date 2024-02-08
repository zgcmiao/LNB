from src.dms.exceptions.base import Error


class ServiceError(Error):
    pass


class AccountServiceError(ServiceError):
    pass


class DataServiceError(ServiceError):
    pass
