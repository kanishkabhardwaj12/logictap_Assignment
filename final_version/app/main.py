from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .database import CallDatabase


class CallRecord(BaseModel):
    call_id: str = Field(..., min_length=1)
    status: str
    duration_secs: int = Field(..., ge=0)


DEFAULT_DATABASE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "calls.db"
)
def create_app(database: CallDatabase) -> FastAPI:
    app = FastAPI(title="Call Records Service - Final Version")

    @app.post(
        "/call-ended",
        response_model=CallRecord,
        status_code=status.HTTP_200_OK,
    )
    def call_ended(call: CallRecord) -> CallRecord:
        stored_call = database.save_if_new(
            call.call_id, call.status, call.duration_secs
        )
        return CallRecord(**stored_call)

    @app.get("/calls/{call_id}", response_model=CallRecord)
    def get_call(call_id: str) -> CallRecord:
        stored_call = database.get(call_id)
        if stored_call is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Call '{call_id}' was not found",
            )

        return CallRecord(**stored_call)

    return app


app = create_app(CallDatabase(DEFAULT_DATABASE_PATH))
