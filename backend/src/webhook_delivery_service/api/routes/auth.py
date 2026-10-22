from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from webhook_delivery_service.api.routes.dependencies import get_auth_service
from webhook_delivery_service.application.services.auth import AuthService
from webhook_delivery_service.domain.exceptions import (
    PasswordMismatchError,
    UserAlreadyExistsError,
)
from webhook_delivery_service.infrastructure.database.user import (
    CreateUserRequest,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def sign_up(
    request: CreateUserRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        user = service.sign_up(
            email=request.email,
            password=request.password,
            confirm_password=request.confirm_password,
        )
        return user

    except PasswordMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc