# Detailed Model Analysis - Evangelism Backend

## Overview
This document provides a comprehensive analysis of all database models in the evangelism backend application. The application uses SQLAlchemy ORM with PostgreSQL and follows a multi-tenant architecture with accounts, users, missions, outreach tracking, and expense management.

---

## 1. BaseModel (`app/models/base.py`)

### Purpose
Abstract base class that provides common fields and functionality for all database models.

### Structure
```python
class BaseModel(Base):
    __abstract__ = True
```

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key identifier | Auto-generated UUID (Python + DB default), indexed |
| `created_at` | DateTime (timezone) | Record creation timestamp | Server default: `now()`, not nullable |
| `updated_at` | DateTime (timezone) | Last modification timestamp | Server default: `now()`, auto-updates on change, not nullable |

### Key Features
- **UUID Primary Keys**: Uses PostgreSQL UUID type for better security and distributed system compatibility
- **Automatic Timestamps**: Both `created_at` and `updated_at` are managed automatically by the database
- **Dual Defaults**: UUID generation happens both in Python (`uuid.uuid4`) and database (`gen_random_uuid()`)
- **Abstract Class**: No table is created for `BaseModel` itself - it's only inherited

### Database Requirements
- PostgreSQL extension: `pgcrypto` (for `gen_random_uuid()`)
- PostgreSQL extension: `uuid-ossp` (alternative UUID generation)

---

## 2. User Model (`app/models/user.py`)

### Purpose
Represents system users who can belong to multiple accounts and participate in missions.

### Table Name
`users`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `full_name` | String(255) | User's full name | Not nullable |
| `email` | String(255) | User's email address | Unique, not nullable, indexed |
| `phone_number` | String(50) | Contact phone number | Nullable |
| `password_hash` | String(255) | Hashed password | Not nullable |
| `is_active` | Boolean | Account activation status | Default: `True`, not nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-Many with Account**: Through `AccountUser` join table
- **Many-to-Many with Mission**: Through `MissionUser` join table

### Key Features
- Email uniqueness enforced at database level
- Email indexed for fast lookups
- Soft delete capability through `is_active` flag
- Password stored as hash (never plain text)

### Use Cases
- User authentication
- Multi-account membership
- Mission participation tracking

---

## 3. Role Model (`app/models/role.py`)

### Purpose
Defines roles within an account (e.g., Admin, Member, Viewer). Roles are account-specific.

### Table Name
`roles`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `name` | String(50) | Role name (e.g., "admin", "member") | Unique, not nullable |
| `account_id` | UUID | Foreign key to accounts | Not nullable, FK to `accounts.id` |
| `description` | String(255) | Role description | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-One with Account**: Each role belongs to one account
- **One-to-Many with AccountUser**: Many users can have this role

### Key Features
- Role names are unique globally (not just per account)
- Account-scoped roles (each account can define its own roles)
- Descriptive text for role documentation

### Use Cases
- Access control within accounts
- Permission management
- User role assignment

---

## 4. Account Model (`app/models/account.py`)

### Purpose
Represents an organization/tenant in the multi-tenant system. Each account can have multiple users, missions, and expenses.

### Table Name
`accounts`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `account_name` | String(255) | Organization name | Not nullable |
| `email` | String(255) | Account contact email | Nullable |
| `phone_number` | String(50) | Account contact phone | Nullable |
| `location` | String(255) | Account location/address | Nullable |
| `created_by` | UUID | Foreign key to users | Not nullable, FK to `users.id` |
| `is_active` | Boolean | Account status | Default: `True`, not nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-One with User**: Created by a user (`created_by`)
- **One-to-Many with AccountUser**: Many user-account associations
- **One-to-Many with Mission**: Account can have multiple missions
- **One-to-Many with Expense**: Account-level expenses
- **One-to-Many with Role**: Account-specific roles

### Key Features
- Multi-tenant architecture foundation
- Tracks creator for audit purposes
- Soft delete via `is_active` flag
- Can have account-level expenses (mission_id = NULL)

### Use Cases
- Organization/Church management
- Multi-tenant data isolation
- Account-level reporting

---

## 5. AccountUser Model (`app/models/account_user.py`)

### Purpose
Join table implementing many-to-many relationship between Users and Accounts, with role assignment.

### Table Name
`account_users`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `account_id` | UUID | Foreign key to accounts | Not nullable, FK to `accounts.id` |
| `user_id` | UUID | Foreign key to users | Not nullable, FK to `users.id` |
| `role_id` | UUID | Foreign key to roles | Not nullable, FK to `roles.id` |
| `deleted_at` | DateTime (timezone) | Soft delete timestamp | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-One with Account**: Each association belongs to one account
- **Many-to-One with User**: Each association belongs to one user
- **Many-to-One with Role**: Each association has one role

### Key Features
- **Soft Delete**: Uses `deleted_at` instead of hard delete
- **Role Assignment**: Each user-account relationship has a specific role
- **Audit Trail**: Tracks when associations are created/updated/deleted

### Use Cases
- User membership in accounts
- Role-based access control per account
- Historical tracking of user-account relationships

### Potential Issues
- No unique constraint on `(account_id, user_id)` - a user could theoretically have multiple active roles in the same account
- Consider adding unique constraint or composite index

---

## 6. Mission Model (`app/models/mission.py`)

### Purpose
Represents evangelism missions organized by accounts. Tracks mission details, budget, location, and timeline.

### Table Name
`missions`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `account_id` | UUID | Foreign key to accounts | Not nullable, FK to `accounts.id` |
| `name` | String(255) | Mission name | Not nullable |
| `start_date` | DateTime (timezone) | Mission start date | Nullable |
| `end_date` | DateTime (timezone) | Mission end date | Nullable |
| `location` | JSON | Mission location data | Nullable (structured JSON) |
| `budget` | Float | Mission budget amount | Nullable |
| `created_by` | UUID | Foreign key to users | Not nullable, FK to `users.id` |
| `deleted_at` | DateTime (timezone) | Soft delete timestamp | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-One with Account**: Mission belongs to one account
- **Many-to-One with User**: Created by a user
- **One-to-Many with MissionUser**: Mission participants
- **One-to-Many with OutreachData**: Outreach records for this mission
- **One-to-One with OutreachNumbers**: Summary statistics (unique constraint)
- **One-to-Many with Expense**: Mission expenses

### Key Features
- **JSON Location**: Flexible location storage (could contain address, coordinates, etc.)
- **Budget Tracking**: Financial planning per mission
- **Soft Delete**: Uses `deleted_at` for data retention
- **Date Range**: Start and end dates for mission timeline

### Use Cases
- Mission planning and management
- Budget allocation
- Participant tracking
- Outreach data collection

---

## 7. MissionUser Model (`app/models/mission_user.py`)

### Purpose
Join table linking users to missions with role assignment (leader, member, guest).

### Table Name
`mission_users`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `mission_id` | UUID | Foreign key to missions | Not nullable, FK to `missions.id` |
| `user_id` | UUID | Foreign key to users | Not nullable, FK to `users.id` |
| `role` | Enum(MissionRole) | User's role in mission | Not nullable |
| `deleted_at` | DateTime (timezone) | Soft delete timestamp | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Enum: MissionRole
```python
class MissionRole(str, enum.Enum):
    LEADER = "leader"
    MEMBER = "member"
    GUEST = "guest"
```

### Relationships
- **Many-to-One with Mission**: Each association belongs to one mission
- **Many-to-One with User**: Each association belongs to one user

### Key Features
- **Enum-based Roles**: Type-safe role assignment
- **Soft Delete**: Historical tracking of participation
- **Mission-specific Roles**: Different from account roles

### Use Cases
- Mission participant management
- Role-based mission permissions
- Participation history

### Potential Issues
- No unique constraint on `(mission_id, user_id)` - could allow duplicate participations
- Consider adding unique constraint

---

## 8. OutreachData Model (`app/models/outreach.py`)

### Purpose
Stores individual outreach contact records (people reached during missions).

### Table Name
`outreach_data`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `account_id` | UUID | Foreign key to accounts | Not nullable, FK to `accounts.id`, indexed |
| `mission_id` | UUID | Foreign key to missions | Not nullable, FK to `missions.id`, indexed |
| `full_name` | String(255) | Contact's full name | Not nullable |
| `phone_number` | String(50) | Contact's phone | Nullable |
| `status` | String(50) | Outreach status | Nullable (e.g., "interested", "saved") |
| `created_by_user_id` | UUID | Foreign key to users | Not nullable, FK to `users.id` |
| `deleted_at` | DateTime (timezone) | Soft delete timestamp | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-One with Mission**: Outreach belongs to one mission
- **Many-to-One with User**: Created by a user

### Key Features
- **Dual Indexing**: Both `account_id` and `mission_id` are indexed for fast queries
- **Status Tracking**: Flexible status field for workflow management
- **Audit Trail**: Tracks who created each outreach record
- **Soft Delete**: Data retention for reporting

### Use Cases
- Contact management
- Evangelism tracking
- Follow-up workflows
- Reporting and analytics

### Potential Improvements
- Consider enum for `status` field instead of free-form string
- Add index on `status` if frequently queried
- Consider adding index on `created_by_user_id`

---

## 9. OutreachNumbers Model (`app/models/outreach.py`)

### Purpose
Stores aggregated statistics for each mission (summary of outreach results).

### Table Name
`outreach_numbers`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `account_id` | UUID | Foreign key to accounts | Not nullable, FK to `accounts.id`, indexed |
| `mission_id` | UUID | Foreign key to missions | Not nullable, FK to `missions.id`, unique, indexed |
| `interested` | Integer | Number of interested contacts | Default: 0, not nullable |
| `healed` | Integer | Number of healed contacts | Default: 0, not nullable |
| `saved` | Integer | Number of saved contacts | Default: 0, not nullable |
| `deleted_at` | DateTime (timezone) | Soft delete timestamp | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **One-to-One with Mission**: Each mission has one summary record (unique constraint on `mission_id`)

### Key Features
- **One-to-One Relationship**: Each mission has exactly one summary record
- **Unique Constraint**: `mission_id` is unique (enforced via index)
- **Aggregated Metrics**: Pre-calculated statistics for performance
- **Default Values**: All counters default to 0

### Use Cases
- Mission performance dashboards
- Quick statistics without aggregation queries
- Reporting and analytics

### Potential Improvements
- Consider adding more metric types (e.g., `baptized`, `follow_up_needed`)
- Consider adding timestamp for when metrics were last updated

---

## 10. Expense Model (`app/models/expense.py`)

### Purpose
Tracks expenses at both account and mission levels.

### Table Name
`expenses`

### Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | UUID | Primary key | Inherited from BaseModel |
| `account_id` | UUID | Foreign key to accounts | Not nullable, FK to `accounts.id` |
| `mission_id` | UUID | Foreign key to missions | Nullable (for account-level expenses), FK to `missions.id` |
| `user_id` | UUID | Foreign key to users | Not nullable, FK to `users.id` |
| `category` | String(100) | Expense category | Not nullable |
| `amount` | Float | Expense amount | Not nullable |
| `description` | String(255) | Expense description | Nullable |
| `deleted_at` | DateTime (timezone) | Soft delete timestamp | Nullable |
| `created_at` | DateTime | Creation timestamp | Inherited from BaseModel |
| `updated_at` | DateTime | Update timestamp | Inherited from BaseModel |

### Relationships
- **Many-to-One with Account**: All expenses belong to an account
- **Many-to-One with Mission**: Optional - expenses can be mission-specific
- **Many-to-One with User**: Tracks who created/recorded the expense

### Key Features
- **Dual-level Expenses**: Can be account-level (`mission_id = NULL`) or mission-specific
- **Category Classification**: Flexible category system
- **Amount Tracking**: Financial tracking with float precision
- **Soft Delete**: Historical financial data retention

### Use Cases
- Budget tracking
- Financial reporting
- Expense categorization
- Mission cost analysis

### Potential Improvements
- Consider enum for `category` for consistency
- Add index on `category` if frequently filtered
- Add index on `mission_id` for mission expense queries
- Consider adding `expense_date` field separate from `created_at`
- Consider using `Decimal` instead of `Float` for currency (better precision)

---

## Database Schema Summary

### Table Relationships Diagram

```
User (1) ──< (N) AccountUser (N) >── (1) Account
                │
                └── (N) >── (1) Role

User (1) ──< (N) MissionUser (N) >── (1) Mission
                                          │
                                          ├── (1) >── (1) OutreachNumbers
                                          │
                                          └── (1) >──< (N) OutreachData
                                          │
                                          └── (1) >──< (N) Expense

Account (1) >──< (N) Mission
Account (1) >──< (N) Expense
Account (1) >──< (N) Role
```

### Indexes Summary

| Table | Indexed Columns | Type |
|-------|----------------|------|
| `users` | `id`, `email` | Primary key, unique index |
| `outreach_data` | `account_id`, `mission_id` | Non-unique indexes |
| `outreach_numbers` | `account_id`, `mission_id` | Non-unique, unique (mission_id) |

### Foreign Key Constraints

| Table | Foreign Keys |
|-------|--------------|
| `accounts` | `created_by` → `users.id` |
| `roles` | `account_id` → `accounts.id` |
| `account_users` | `account_id` → `accounts.id`, `user_id` → `users.id`, `role_id` → `roles.id` |
| `missions` | `account_id` → `accounts.id`, `created_by` → `users.id` |
| `mission_users` | `mission_id` → `missions.id`, `user_id` → `users.id` |
| `outreach_data` | `account_id` → `accounts.id`, `mission_id` → `missions.id`, `created_by_user_id` → `users.id` |
| `outreach_numbers` | `account_id` → `accounts.id`, `mission_id` → `missions.id` (unique) |
| `expenses` | `account_id` → `accounts.id`, `mission_id` → `missions.id`, `user_id` → `users.id` |

### Soft Delete Pattern

Tables using soft delete (via `deleted_at`):
- `account_users`
- `missions`
- `mission_users`
- `outreach_data`
- `outreach_numbers`
- `expenses`

Tables using hard delete or `is_active` flag:
- `users` (uses `is_active`)
- `accounts` (uses `is_active`)
- `roles` (no soft delete)

---

## Recommendations

### 1. Add Unique Constraints
- `account_users`: Add unique constraint on `(account_id, user_id)` where `deleted_at IS NULL`
- `mission_users`: Add unique constraint on `(mission_id, user_id)` where `deleted_at IS NULL`

### 2. Add Missing Indexes
- `expenses.mission_id` (for mission expense queries)
- `expenses.category` (if frequently filtered)
- `outreach_data.created_by_user_id` (for user activity tracking)
- `outreach_data.status` (if frequently queried)

### 3. Consider Enums
- `outreach_data.status` → Create `OutreachStatus` enum
- `expenses.category` → Create `ExpenseCategory` enum

### 4. Data Type Improvements
- `expenses.amount` → Consider `Decimal` for currency precision
- Add `expense_date` field to `expenses` separate from `created_at`

### 5. Validation
- Add check constraint: `missions.end_date >= missions.start_date`
- Add check constraint: `expenses.amount > 0`

---

## Migration Strategy

The existing migration (`eebdf320e015`) appears incomplete - it only adds some foreign keys and indexes but doesn't create the base tables. A complete migration should:

1. Create PostgreSQL extensions (`uuid-ossp`, `pgcrypto`)
2. Create all tables with proper columns
3. Add all foreign key constraints
4. Add all indexes
5. Add any check constraints
6. Set up proper defaults and server defaults

