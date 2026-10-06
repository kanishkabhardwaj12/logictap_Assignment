from threading import Lock

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class CallRecord(BaseModel):
    call_id: str = Field(..., min_length=1)
    status: str
    duration_secs: int = Field(..., ge=0)


app = FastAPI(title="Call Records Service")

_calls: dict[str, CallRecord] = {}
_calls_lock = Lock()


@app.post(
    "/call-ended",
    response_model=CallRecord,
    status_code=status.HTTP_200_OK,
)
def call_ended(call: CallRecord) -> CallRecord:
    """Store a call once, returning the existing record for duplicates."""
    with _calls_lock:
        existing_call = _calls.get(call.call_id)
        if existing_call is not None:
            return existing_call

        _calls[call.call_id] = call
        return call


@app.get("/calls/{call_id}", response_model=CallRecord)
def get_call(call_id: str) -> CallRecord:
    with _calls_lock:
        call = _calls.get(call_id)

    if call is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Call '{call_id}' was not found",
        )

    return call
