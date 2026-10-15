from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AccessDeniedException,
    AuthenticationFailedException,
    BaseAppException,
    BusinessRuleViolationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    InvalidForeignKeyException,
)

STATUS_CODES: list[tuple[type[BaseAppException], int]] = [
    (EntityNotFoundException, status.HTTP_404_NOT_FOUND),
    (EntityAlreadyExistsException, status.HTTP_409_CONFLICT),
    (AuthenticationFailedException, status.HTTP_401_UNAUTHORIZED),
    (AccessDeniedException, status.HTTP_403_FORBIDDEN),
    (InvalidForeignKeyException, status.HTTP_400_BAD_REQUEST),
    (BusinessRuleViolationException, status.HTTP_400_BAD_REQUEST),
]

app = FastAPI(title=settings.app.NAME, version=settings.app.VERSION)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.app.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
)


@app.exception_handler(BaseAppException)
async def app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """Преобразовать исключения бизнес-логики в HTTP-ответы."""

    status_code = next(
        (
            code
            for exception_type, code in STATUS_CODES
            if isinstance(exc, exception_type)
        ),
        status.HTTP_400_BAD_REQUEST,
    )

    return JSONResponse(status_code=status_code, content={"detail": exc.detail})


@app.get("/health", tags=["health"])
def check_health() -> dict:
    """Проверяет работоспособность сервера."""

    return {"status": "Ок"}


app.include_router(api_router)
