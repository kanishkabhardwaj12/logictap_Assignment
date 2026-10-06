# Call Records Service - Final Version

This version keeps the Version 1 API but stores records in SQLite, so records
survive application restarts. The database uses `call_id` as its primary key,
which prevents duplicate records at the database level. Duplicate POST
requests return the original stored record.

## Run locally

From the `final_version` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, and interactive
documentation is available at `http://127.0.0.1:8000/docs`.

The default SQLite database is created at `data/calls.db`.

## API examples

```bash
curl -X POST http://127.0.0.1:8000/call-ended \
  -H 'Content-Type: application/json' \
  -d '{"call_id":"abc123","status":"answered","duration_secs":42}'

curl http://127.0.0.1:8000/calls/abc123
```

## Run tests

```bash
pytest
```
