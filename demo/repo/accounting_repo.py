from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

# from account.entity.accounting_entity import (
# 	AccountingEntryEntity,
# 	AccountingMonthlyCategoryStatsEntity,
# 	AccountingUserEntity,
# )


class AccountingRepo:
	def __init__(self, postgres_session: Session):
		"""Use the request-scoped SQLAlchemy session for every repository operation."""
		self.postgres_session = postgres_session
	# 
	# def get_user_by_username(
	# 	self,
	# 	tenant_key: str,
	# 	username: str,
	# ) -> AccountingUserEntity | None:
	# 	"""Return one tenant user by username when it exists."""
	# 	return (
	# 		self.postgres_session.query(AccountingUserEntity)
	# 		.filter(
	# 			AccountingUserEntity.tenant_key == tenant_key,
	# 			AccountingUserEntity.username == username,
	# 		)
	# 		.one_or_none()
	# 	)
	# 
	# def add_user(
	# 	self,
	# 	tenant_key: str,
	# 	username: str,
	# 	password_salt: str,
	# 	password_md5: str,
	# 	create_at: datetime,
	# ) -> AccountingUserEntity:
	# 	"""Add one tenant user to the current request transaction."""
	# 	user_entity = AccountingUserEntity(
	# 		tenant_key=tenant_key,
	# 		username=username,
	# 		password_salt=password_salt,
	# 		password_md5=password_md5,
	# 		create_at=create_at,
	# 	)
	# 	self.postgres_session.add(user_entity)
	# 	return user_entity
	# 
	# def update_user_password(
	# 	self,
	# 	user_entity: AccountingUserEntity,
	# 	password_salt: str,
	# 	password_md5: str,
	# ) -> AccountingUserEntity:
	# 	"""Replace an attached user's password within the request transaction."""
	# 	user_entity.password_salt = password_salt
	# 	user_entity.password_md5 = password_md5
	# 	self.postgres_session.add(user_entity)
	# 	return user_entity
	# 
	# def add_entries(
	# 	self,
	# 	entry_entities: list[AccountingEntryEntity],
	# ) -> list[AccountingEntryEntity]:
	# 	"""Add classified entries and invalidate affected closed-month snapshots."""
	# 	closed_months = {
	# 		entry_entity.account_date.strftime("%Y-%m")
	# 		for entry_entity in entry_entities
	# 		if entry_entity.account_date.strftime("%Y-%m") < date.today().strftime("%Y-%m")
	# 	}
	# 	if closed_months:
	# 		tenant_keys = {entry_entity.tenant_key for entry_entity in entry_entities}
	# 		self.postgres_session.query(AccountingMonthlyCategoryStatsEntity).filter(
	# 			AccountingMonthlyCategoryStatsEntity.tenant_key.in_(tenant_keys),
	# 			AccountingMonthlyCategoryStatsEntity.month.in_(closed_months),
	# 		).delete(synchronize_session=False)
	# 	self.postgres_session.add_all(entry_entities)
	# 	return entry_entities
