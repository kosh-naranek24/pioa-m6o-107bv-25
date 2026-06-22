# src/db/backend/file.py
import json
from pathlib import Path
from typing import Union

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table

class FileDatabase(Database):
    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(
                f"Таблица '{table_name}' не существует."
            )

        try:
            with table_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' содержит некорректный JSON."
            ) from error
        except OSError as error:
            raise InvalidStorageDataError(
                f"Ошибка при чтении файла таблицы '{table_name}': {error}"
            ) from error

        return self._deserialize_table(data, table_name)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        temp_path = table_path.with_suffix(".tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._serialize_table(table),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            temp_path.replace(table_path)

        except OSError as error:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

            raise InvalidStorageDataError(
                f"Ошибка при сохранении таблицы '{table_name}': {error}"
            ) from error

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"

    def _serialize_table(self, table: Table) -> dict:
        return {
            "columns": list(table.columns),
            "records": [record.copy() for record in table.records],
        }

    def _deserialize_table(self, data: dict, table_name: str) -> Table:

        if "columns" not in data:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' не содержит поле 'columns'."
            )

        if "records" not in data:
            raise InvalidStorageDataError(
                f"Файл таблицы '{table_name}' не содержит поле 'records'."
            )

        # Проверяем тип columns
        if not isinstance(data["columns"], list):
            raise InvalidStorageDataError(
                f"Поле 'columns' в таблице '{table_name}' должно быть списком, "
                f"получено {type(data['columns']).__name__}."
            )

        # Проверяем тип records
        if not isinstance(data["records"], list):
            raise InvalidStorageDataError(
                f"Поле 'records' в таблице '{table_name}' должно быть списком, "
                f"получено {type(data['records']).__name__}."
            )

        # Проверяем, что columns не пустой
        if not data["columns"]:
            raise InvalidStorageDataError(
                f"Список колонок в таблице '{table_name}' не может быть пустым."
            )


        for i, column in enumerate(data["columns"]):
            if not isinstance(column, str):
                raise InvalidStorageDataError(
                    f"Колонка #{i} в таблице '{table_name}' должна быть строкой, "
                    f"получено {type(column).__name__}."
                )

        columns = tuple(data["columns"])
        records = data["records"]

        validated_records = []
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                raise InvalidStorageDataError(
                    f"Запись #{i} в таблице '{table_name}' должна быть словарем, "
                    f"получено {type(record).__name__}."
                )

            for key in record.keys():
                if not isinstance(key, str):
                    raise InvalidStorageDataError(
                        f"Ключ '{key}' в записи #{i} таблицы '{table_name}' "
                        f"должен быть строкой, получено {type(key).__name__}."
                    )

            missing_columns = [col for col in columns if col not in record]
            if missing_columns:
                raise InvalidStorageDataError(
                    f"В записи #{i} таблицы '{table_name}' отсутствуют колонки: "
                    f"{', '.join(missing_columns)}."
                )

            extra_keys = [key for key in record.keys() if key not in columns]
            if extra_keys:
                raise InvalidStorageDataError(
                    f"В записи #{i} таблицы '{table_name}' обнаружены лишние ключи: "
                    f"{', '.join(extra_keys)}."
                )

            validated_records.append(record)

        return Table(columns, validated_records)