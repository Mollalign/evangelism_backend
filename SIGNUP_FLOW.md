# Signup Flow Documentation

## How Signup Works

### Frontend Flow (Flutter App)

1. **User fills out signup form** (`lib/ui/auth/signup_screen.dart`)
   - Full Name (required)
   - Email (required, validated)
   - Phone Number (optional)
   - Password (required, min 8 characters)
   - Confirm Password (must match)

2. **Form validation**
   - Email format validation
   - Password strength validation
   - Password match validation

3. **API call** (`lib/providers/auth_provider.dart`)
   ```dart
   await ref.read(authNotifierProvider.notifier).register({
     'full_name': _fullNameController.text.trim(),
     'email': _emailController.text.trim(),
     'password': _passwordController.text,
     if (_phoneController.text.isNotEmpty)
       'phone_number': _phoneController.text.trim(),
   });
   ```

4. **Repository layer** (`lib/data/repositories/auth_repository.dart`)
   - Sends POST request to `/api/v1/auth/register`
   - Includes user data in request body

### Backend Flow (FastAPI)

1. **API Endpoint** (`app/api/v1/auth.py`)
   - Receives POST request at `/api/v1/auth/register`
   - Validates request body against `UserRegister` schema

2. **Auth Service** (`app/services/auth.py`)
   - Checks if email already exists
   - Hashes password using bcrypt
   - Creates user record in database
   - Generates JWT access and refresh tokens

3. **User Repository** (`app/repositories/user.py`)
   - Creates new `User` record with:
     - email
     - password_hash (hashed)
     - full_name
     - phone_number (optional)
     - is_active = True

4. **Response**
   - Returns `AuthResponse` with:
     - User object
     - access_token (JWT)
     - refresh_token (JWT)
     - token_type = "bearer"

### Data Flow Diagram

```
User Input → Form Validation → AuthProvider → AuthRepository
    ↓
API Request → FastAPI Endpoint → AuthService → UserRepository
    ↓
Database (Create User) → Generate Tokens → Return Response
    ↓
Frontend (Store Tokens) → Navigate to Dashboard
```

## Default Seeded Data

After running the seed script, you'll have:

### Users
- **Admin**: `admin@cmoms.com` / `admin123`
- **Missionary**: `missionary@cmoms.com` / `missionary123`
- **Test**: `test@cmoms.com` / `test123`

### Account
- **CMOMS Main Account** (linked to all users)

### Roles
- **admin** (full access)
- **missionary** (field worker access)

### Sample Missions
- **Addis Ababa Outreach 2024** (with location data)
- **Rural Evangelism Campaign** (with location data)

### Sample Data
- 3 outreach contacts
- Outreach numbers (interested: 15, heard: 25, saved: 8)
- 3 sample expenses

## Running the Seed Script

```bash
cd /home/mollalgn/Desktop/Hackaton/evangelism_backend
source venv/bin/activate  # If using virtual environment
python scripts/seed_data.py
```

## Notes

- The seed script is **idempotent** - it won't create duplicates if run multiple times
- Passwords are hashed using bcrypt before storage
- All users are created with `is_active=True`
- The script creates relationships between users, accounts, and roles

