# Call Records Service

A small local FastAPI service that stores call-ended records in memory. A
`call_id` is idempotent: sending it more than once returns the original record
without replacing it.

## Requirements

- Python 3.9+

## Run locally

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The service is available at `http://127.0.0.1:8000`. Interactive API
documentation is at `http://127.0.0.1:8000/docs`.

Records are held in process memory and are lost when the server stops.

## API

### Store a call

```bash
curl -X POST http://127.0.0.1:8000/call-ended \
  -H 'Content-Type: application/json' \
  -d '{"call_id":"abc123","status":"answered","duration_secs":42}'
```

The endpoint returns `200 OK` and the stored record. A request without
`call_id` returns `422 Unprocessable Entity` with a validation error identifying
`call_id`.

### Get a call

```bash
curl http://127.0.0.1:8000/calls/abc123
```

An unknown call returns `404 Not Found`.

## Run tests

```bash
pytest
```
