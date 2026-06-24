from sqlalchemy import create_engine, inspect, text

from app.config import get_settings

TIME_COLUMNS = ("created_at", "updated_at")


def main() -> None:
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in inspector.get_table_names():
            columns = {column["name"] for column in inspector.get_columns(table)}
            updates = [column for column in TIME_COLUMNS if column in columns]
            if not updates:
                continue
            set_clause = ", ".join(f"`{column}` = DATE_ADD(`{column}`, INTERVAL 8 HOUR)" for column in updates)
            result = conn.execute(text(f"UPDATE `{table}` SET {set_clause}"))
            print(f"{table}: {result.rowcount}")


if __name__ == "__main__":
    main()
