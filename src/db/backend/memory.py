# src/db/backend/memory.py

from .database import Database
from .errors import TableNotFoundError
from .table import Table


class MemoryDatabase(Database):
    """База данных в оперативной памяти."""

    def __init__(self) -> None:
        self._tables: dict[str, Table] = {}

    def _table_exists(self, table_name: str) -> bool:
        return table_name in self._tables

    def _load_table(self, table_name: str) -> Table:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Table '{table_name}' does not exist.")
        return self._tables[table_name]

    def _save_table(self, table_name: str, table: Table) -> None:
        self._tables[table_name] = table