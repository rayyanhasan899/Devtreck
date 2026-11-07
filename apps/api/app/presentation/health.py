from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_session

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "devtreck-api"


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Process liveness only; database readiness arrives in phase 2."""
    return HealthResponse()


@router.get("/ready", response_model=HealthResponse, tags=["health"])
def ready(session: Annotated[Session, Depends(get_session)]) -> HealthResponse:
    session.execute(text("SELECT 1"))
    return HealthResponse()
