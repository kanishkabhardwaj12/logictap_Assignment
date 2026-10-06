import sqlite3
from pathlib import Path
from typing import Dict, Optional, Union


class CallDatabase:
    def __init__(self, path: Union[str, Path]) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS calls (
                    call_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    duration_secs INTEGER NOT NULL
                )
                """
            )

    def save_if_new(
        self, call_id: str, status: str, duration_secs: int
    ) -> Dict[str, object]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO calls (call_id, status, duration_secs)
                VALUES (?, ?, ?)
                """,
                (call_id, status, duration_secs),
            )
            row = connection.execute(
                """
                SELECT call_id, status, duration_secs
                FROM calls
                WHERE call_id = ?
                """,
                (call_id,),
            ).fetchone()

        if row is None:
            raise RuntimeError(f"Could not save call '{call_id}'")
        return dict(row)

    def get(self, call_id: str) -> Optional[Dict[str, object]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT call_id, status, duration_secs
                FROM calls
                WHERE call_id = ?
                """,
                (call_id,),
            ).fetchone()

        return dict(row) if row is not None else None
