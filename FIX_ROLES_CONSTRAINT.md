# Fix: Roles Unique Constraint Issue

## Problem
The `roles` table had a unique constraint on `name` only, which prevented multiple accounts from having roles with the same name (e.g., "admin"). This is incorrect for a SaaS multi-tenant system where each account should have its own set of roles.

## Error
```
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint "roles_name_key"
DETAIL: Key (name)=(admin) already exists.
```

## Solution

### 1. Updated Role Model
Changed from:
```python
name = Column(String(50), unique=True, nullable=False)
```

To:
```python
__table_args__ = (
    UniqueConstraint('name', 'account_id', name='unique_role_per_account'),
)
name = Column(String(50), nullable=False)
```

This makes roles unique per account, not globally unique.

### 2. Database Migration
Created migration `fix_roles_unique_constraint.py` that:
- Drops the old `roles_name_key` constraint (unique on name only)
- Creates new `unique_role_per_account` constraint (unique on name + account_id)

### 3. Added Safety Check
Updated `auth_service.register()` to check if role exists before creating:
```python
existing_role = await role_repo.get_by_name_and_account("admin", str(account.id))
if existing_role:
    default_role = existing_role
else:
    default_role = await role_repo.create(...)
```

## Status
✅ Migration applied successfully
✅ Model updated
✅ Registration should now work for multiple accounts

## Testing
Try registering a new user - it should now create the account and "admin" role without constraint violations.
