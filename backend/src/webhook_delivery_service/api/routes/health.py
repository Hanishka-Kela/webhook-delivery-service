from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness():
    return {"status": "ok"}
