# Database Seeding Guide

## How to Run the Seed Script

### Prerequisites
1. Make sure your database is set up and migrations are run
2. Ensure your `.env` file has the correct `DATABASE_URL`

### Steps

1. **Activate virtual environment** (if using one):
   ```bash
   cd /home/mollalgn/Desktop/Hackaton/evangelism_backend
   source venv/bin/activate
   ```

2. **Run the seed script**:
   ```bash
   python scripts/seed_data.py
   ```
   
   Or if `python` is not available:
   ```bash
   python3 scripts/seed_data.py
   ```

3. **Verify the data**:
   - Check your database to see the seeded data
   - Or test login with the default credentials

## What Gets Created

### Users (3)
- **Admin**: `admin@cmoms.com` / `admin123`
- **Missionary**: `missionary@cmoms.com` / `missionary123`
- **Test**: `test@cmoms.com` / `test123`

### Account (1)
- **CMOMS Main Account** (linked to all users)

### Roles (2)
- **admin** - Full access
- **missionary** - Field worker access

### Missions (2)
- **Addis Ababa Outreach 2024** (with location coordinates)
- **Rural Evangelism Campaign** (with location coordinates)

### Sample Data
- 3 outreach contacts
- Outreach numbers (interested: 15, heard: 25, saved: 8)
- 3 sample expenses

## Important Notes

- The script is **idempotent** - safe to run multiple times
- It checks if data exists before creating (won't create duplicates)
- All passwords are hashed using bcrypt
- All users are created with `is_active=True`

## Troubleshooting

If you get errors:
1. Check your database connection in `.env`
2. Make sure migrations are run: `alembic upgrade head`
3. Check that all required models are imported correctly
4. Verify PostgreSQL extensions are installed (uuid-ossp, pgcrypto)

