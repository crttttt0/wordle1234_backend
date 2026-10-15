class BaseAppException(Exception):
    """Базовое исключение бизнес-логики приложения"""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class InvalidForeignKeyException(BaseAppException):
    """Переданный FK-идентификатор ссылается на несуществующую запись"""

    pass


class EntityNotFoundException(BaseAppException):
    """Какая-то сущность не найдена"""

    pass


class EntityAlreadyExistsException(BaseAppException):
    """Попытка создать дубликат уникальных данных"""

    pass


class AuthenticationFailedException(BaseAppException):
    """Пользователь ввел неверный пароль или логин"""

    pass


class AccessDeniedException(BaseAppException):
    """У пользователя недостаточно прав для этого действия"""

    pass


class BusinessRuleViolationException(BaseAppException):
    """Нарушено какое-то внутреннее правило"""

    pass
