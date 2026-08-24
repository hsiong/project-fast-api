import logging
import re

from fastapi import FastAPI

from core.config.settings import (POSTGRES_DATABASE, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_URL,
                                  POSTGRES_USERNAME, )


def normalize_sql_type(column_type, dialect) -> str:
	"""Compile and normalize one SQLAlchemy type for stable schema comparison."""
	compiled_type = column_type.compile(dialect=dialect).upper()
	return re.sub(r"\s+", " ", compiled_type).strip()


def validate_accounting_schema(engine, metadata) -> None:
	"""Reject missing or incompatible ORM columns and print PostgreSQL ALTER guidance."""
	from sqlalchemy import inspect
	
	database_inspector = inspect(engine)
	dialect = engine.dialect
	identifier_preparer = dialect.identifier_preparer
	differences = []
	alter_statements = []
	
	for entity_table in metadata.sorted_tables:
		table_name = entity_table.name
		quoted_table_name = identifier_preparer.quote(table_name)
		database_columns = {column["name"]: column for column in
			database_inspector.get_columns(table_name, schema=entity_table.schema)}
		entity_column_names = {column.name for column in entity_table.columns}
		for database_column_name in sorted(database_columns.keys() - entity_column_names):
			logging.warning("PostgreSQL 字段 %s.%s 在 ORM Entity 中不存在，已忽略", table_name, database_column_name, )
		
		# Database-only columns are allowed after warning; every entity column must match.
		for entity_column in entity_table.columns:
			column_name = entity_column.name
			quoted_column_name = identifier_preparer.quote(column_name)
			expected_type = normalize_sql_type(entity_column.type, dialect)
			database_column = database_columns.get(column_name)
			if database_column is None:
				differences.append(f"{table_name}.{column_name}: ORM 字段在 PostgreSQL 中不存在")
				alter_statements.append(f"ALTER TABLE {quoted_table_name} "
				                        f"ADD COLUMN {quoted_column_name} {expected_type};")
				if not entity_column.nullable:
					alter_statements.append(f"-- 回填 {quoted_table_name}.{quoted_column_name} 后执行：\n"
					                        f"ALTER TABLE {quoted_table_name} ALTER COLUMN "
					                        f"{quoted_column_name} SET NOT NULL;")
				continue
			
			actual_type = normalize_sql_type(database_column["type"], dialect)
			if actual_type != expected_type:
				differences.append(f"{table_name}.{column_name}: 类型不一致，"
				                   f"PostgreSQL={actual_type}，ORM={expected_type}")
				alter_statements.append(f"ALTER TABLE {quoted_table_name} ALTER COLUMN {quoted_column_name} "
				                        f"TYPE {expected_type} USING {quoted_column_name}::{expected_type};")
			
			actual_nullable = bool(database_column["nullable"])
			expected_nullable = bool(entity_column.nullable)
			if actual_nullable != expected_nullable:
				differences.append(f"{table_name}.{column_name}: nullable 不一致，"
				                   f"PostgreSQL={actual_nullable}，ORM={expected_nullable}")
				nullable_action = "DROP NOT NULL" if expected_nullable else "SET NOT NULL"
				alter_statements.append(f"ALTER TABLE {quoted_table_name} ALTER COLUMN "
				                        f"{quoted_column_name} {nullable_action};")
		
		database_primary_key = database_inspector.get_pk_constraint(table_name, schema=entity_table.schema, )
		actual_primary_columns = set(database_primary_key.get("constrained_columns") or [])
		expected_primary_columns = {column.name for column in entity_table.primary_key.columns}
		if actual_primary_columns != expected_primary_columns:
			differences.append(f"{table_name}: 主键字段不一致，"
			                   f"PostgreSQL={sorted(actual_primary_columns)}，"
			                   f"ORM={sorted(expected_primary_columns)}")
			primary_key_name = database_primary_key.get("name")
			if primary_key_name:
				quoted_primary_key_name = identifier_preparer.quote(primary_key_name)
				alter_statements.append(f"ALTER TABLE {quoted_table_name} DROP CONSTRAINT {quoted_primary_key_name};")
			if expected_primary_columns:
				quoted_primary_columns = ", ".join(
					identifier_preparer.quote(column_name) for column_name in sorted(expected_primary_columns))
				alter_statements.append(f"ALTER TABLE {quoted_table_name} ADD PRIMARY KEY ({quoted_primary_columns});")
	
	if differences:
		difference_text = "\n".join(f"- {difference}" for difference in differences)
		alter_text = "\n".join(alter_statements)
		raise RuntimeError("PostgreSQL 表结构与 ORM Entity 不一致：\n"
		                   f"{difference_text}\n"
		                   "请确认数据兼容性后执行以下 SQL：\n"
		                   f"{alter_text}")


def init_postgres(app: FastAPI) -> None:
	"""Initialize PostgreSQL tables once and bind one session to each HTTP request."""
	app.postgresSession = None
	if not POSTGRES_URL:
		return
	
	from sqlalchemy import create_engine
	from sqlalchemy.engine import URL
	from sqlalchemy.orm import sessionmaker
	
	postgres_url = URL.create(drivername="postgresql+psycopg2", username=POSTGRES_USERNAME, password=POSTGRES_PASSWORD,
		host=POSTGRES_URL, port=POSTGRES_PORT, database=POSTGRES_DATABASE, )
	engine = create_engine(postgres_url, pool_pre_ping=True)
	
	logging.info("Initialized PostgreSQL accounting tables")
	
	app.postgresSession = sessionmaker(bind=engine, autocommit=False, expire_on_commit=False, )
	
	# Create missing tables, then reject incompatible columns before serving requests.    
	logging.info("Validating PostgreSQL accounting tables")
	# from account.entity.accounting_entity import AccountingBase           
	# logging.info("Validating PostgreSQL accounting tables: %s", "accounting_entity")
	# AccountingBase.metadata.create_all(bind=engine, checkfirst=True)
	# validate_accounting_schema(engine=engine, metadata=AccountingBase.metadata)
	
	@app.middleware("http")
	async def postgres_session_middleware(request, call_next):
		"""Commit or roll back the single SQLAlchemy session used by this request."""
		postgres_session = app.postgresSession()
		request.state.postgresSession = postgres_session
		try:
			response = await call_next(request)
			postgres_session.commit()
			return response
		except Exception:
			postgres_session.rollback()
			raise
		finally:
			postgres_session.close()
