from sqlalchemy import create_engine, text
from storage.config_store import get_setting


def build_url(db_type: str, host: str, port: str, name: str, user: str, password: str) -> str:
    if db_type == "mysql":
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

def get_engine():
    db_type = get_setting("db_type", "postgresql")
    host = get_setting("db_host", "localhost")
    port = get_setting("db_port", "5432")
    name = get_setting("db_name", "")
    user = get_setting("db_user", "")
    password = get_setting("db_password", "")
    return create_engine(build_url(db_type, host, port, name, user, password))


def apply_sql(sql: str) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))


def get_schema():
    db_type = get_setting("db_type", "postgresql")
    engine = get_engine()

    if db_type == "mysql":
        return _get_schema_mysql(engine)
    return _get_schema_postgresql(engine)


def _get_schema_postgresql(engine):
    with engine.connect() as conn:
        columns = conn.execute(text("""
            SELECT table_name, column_name, data_type, is_nullable, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)).fetchall()

        primary_keys = conn.execute(text("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = 'public'
        """)).fetchall()

        foreign_keys = conn.execute(text("""
            SELECT
                kcu.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
        """)).fetchall()

    return _build_tables(columns, primary_keys, foreign_keys)


def _get_schema_mysql(engine):
    with engine.connect() as conn:
        db_name = get_setting("db_name", "")

        columns = conn.execute(text("""
            SELECT table_name, column_name, data_type, is_nullable, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = :db
            ORDER BY table_name, ordinal_position
        """), {"db": db_name}).fetchall()

        primary_keys = conn.execute(text("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = :db
        """), {"db": db_name}).fetchall()

        foreign_keys = conn.execute(text("""
            SELECT
                kcu.table_name,
                kcu.column_name,
                kcu.referenced_table_name AS foreign_table,
                kcu.referenced_column_name AS foreign_column
            FROM information_schema.key_column_usage kcu
            WHERE kcu.table_schema = :db
            AND kcu.referenced_table_name IS NOT NULL
        """), {"db": db_name}).fetchall()

    return _build_tables(columns, primary_keys, foreign_keys)


def _build_tables(columns, primary_keys, foreign_keys) -> dict:
    pks = {(t, c) for t, c in primary_keys}
    fks = {}
    for table, column, ftable, fcolumn in foreign_keys:
        fks[(table, column)] = {"references_table": ftable, "references_column": fcolumn}

    tables = {}
    for table, column, dtype, nullable, max_length in columns:
        if table not in tables:
            tables[table] = {"columns": [], "foreign_keys": []}
        tables[table]["columns"].append({
            "column": column,
            "type": dtype,
            "nullable": nullable == "YES",
            "primary_key": (table, column) in pks,
            "foreign_key": fks.get((table, column)),
            "max_length": max_length
        })

    for table, column, ftable, fcolumn in foreign_keys:
        tables[table]["foreign_keys"].append(
            f"{table}.{column} → {ftable}.{fcolumn}"
        )

    return tables
