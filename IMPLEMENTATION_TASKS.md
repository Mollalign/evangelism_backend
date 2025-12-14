# Implementation Tasks for SaaS Authentication

## Backend Tasks

### Task 1: Create Account on Registration
**File:** `app/services/auth.py`
**Priority:** HIGH
**Status:** TODO

- [ ] Import AccountRepository, AccountUserRepository, RoleRepository
- [ ] After user creation, create Account
- [ ] Create default "admin" role for account
- [ ] Create AccountUser relationship
- [ ] Include account_id in JWT token

### Task 2: Add Account Context to JWT
**File:** `app/core/security.py`
**Priority:** HIGH
**Status:** TODO

- [ ] Add `account_id` parameter to `create_token_pair()`
- [ ] Include account_id in token payload
- [ ] Update all token creation calls to include account_id

### Task 3: Implement Account Access Verification
**File:** `app/core/dependencies.py`
**Priority:** HIGH
**Status:** TODO

- [ ] Implement `verify_account_access()` function
- [ ] Check AccountUser relationship exists
- [ ] Validate account is active
- [ ] Return Account object on success

### Task 4: Create Get User Accounts Endpoint
**File:** `app/api/v1/users.py`
**Priority:** MEDIUM
**Status:** TODO

- [ ] Create GET `/api/v1/users/accounts` endpoint
- [ ] Query AccountUser for current user
- [ ] Return list of accounts user belongs to
- [ ] Include role information

### Task 5: Create Account Switching Endpoint
**File:** `app/api/v1/auth.py`
**Priority:** MEDIUM
**Status:** TODO

- [ ] Create POST `/api/v1/auth/switch-account/{account_id}` endpoint
- [ ] Verify user has access to account
- [ ] Create new token with new account_id
- [ ] Return new tokens

### Task 6: Add Account Scoping to All Endpoints
**Files:** All API endpoint files
**Priority:** HIGH
**Status:** TODO

- [ ] Add `verify_account_access` dependency to all endpoints
- [ ] Ensure account_id in request matches token's account_id
- [ ] Filter all queries by account_id

### Task 7: Create AccountUser Repository
**File:** `app/repositories/account_user.py`
**Priority:** HIGH
**Status:** TODO

- [ ] Create AccountUserRepository class
- [ ] Add `get_by_user_id()` method
- [ ] Add `get_by_user_and_account()` method
- [ ] Add `create()` method

### Task 8: Create Role Repository
**File:** `app/repositories/role.py`
**Priority:** MEDIUM
**Status:** TODO

- [ ] Create RoleRepository class
- [ ] Add methods for role management

## Frontend Tasks

### Task 1: Update Auth Repository
**File:** `lib/data/repositories/auth_repository.dart`
**Priority:** MEDIUM
**Status:** TODO

- [ ] Add `getUserAccounts()` method
- [ ] Add `switchAccount()` method

### Task 2: Create Account Provider
**File:** `lib/providers/account_provider.dart`
**Priority:** MEDIUM
**Status:** TODO

- [ ] Create AccountNotifier provider
- [ ] Create currentAccountId provider (extract from token or state)
- [ ] Add account switching logic

### Task 3: Update Current Account ID Provider
**File:** `lib/providers/auth_provider.dart`
**Priority:** HIGH
**Status:** TODO

- [ ] Remove hardcoded 'default_account_id'
- [ ] Extract account_id from JWT token
- [ ] Or get from first account in user's account list

### Task 4: Create Account Switcher UI
**File:** `lib/ui/widgets/account_switcher.dart`
**Priority:** MEDIUM
**Status:** TODO

- [ ] Create dropdown/selector widget
- [ ] Show current account name
- [ ] Allow switching between accounts
- [ ] Handle loading/error states

### Task 5: Add Account Switcher to App Bar
**Files:** Admin and Missionary screens
**Priority:** LOW
**Status:** TODO

- [ ] Add AccountSwitcher to AppBar
- [ ] Show in profile screen
- [ ] Handle account switching gracefully

## Database Tasks

### Task 1: Add Unique Constraint
**Priority:** HIGH
**Status:** TODO

```sql
ALTER TABLE account_users 
ADD CONSTRAINT unique_user_account UNIQUE (user_id, account_id);
```

### Task 2: Add Indexes
**Priority:** MEDIUM
**Status:** TODO

```sql
CREATE INDEX idx_account_users_user_id ON account_users(user_id);
CREATE INDEX idx_account_users_account_id ON account_users(account_id);
```

## Testing Tasks

### Task 1: Test Registration Flow
- [ ] User registration creates account
- [ ] AccountUser relationship created
- [ ] Default role assigned
- [ ] Token includes account_id

### Task 2: Test Account Access
- [ ] User can only access their accounts
- [ ] Cannot access other accounts' data
- [ ] Account switching works

### Task 3: Test Multi-Account User
- [ ] User with multiple accounts can switch
- [ ] Data is properly isolated per account
- [ ] Token updates correctly on switch
