#!/bin/bash
echo "=== COMPLETE DATABASE SETUP FOR RAJA RAM REAL ESTATE ==="

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 16 | tr -d '/+' | cut -c1-16)
echo "Generated Database Password: $DB_PASSWORD"

echo ""
echo "1. Checking PostgreSQL status..."
if brew services list | grep -q "postgresql.*started"; then
    echo "   ✅ PostgreSQL is running"
else
    echo "   ⚠️  PostgreSQL is not running, starting..."
    brew services start postgresql@14
    sleep 5
fi

echo ""
echo "2. Creating databases..."
for db in realtorrajaram_prod realtorrajaram_dev realtorrajaram_test; do
    createdb $db 2>/dev/null && echo "   ✅ Created: $db" || echo "   ⚠️  Database $db already exists"
done

echo ""
echo "3. Creating database user..."
psql postgres -c "DROP USER IF EXISTS realtorrajaram_user;" 2>/dev/null
psql postgres -c "CREATE USER realtorrajaram_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ User 'realtorrajaram_user' created"
    
    echo ""
    echo "4. Granting privileges..."
    for db in realtorrajaram_prod realtorrajaram_dev realtorrajaram_test; do
        psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $db TO realtorrajaram_user;" 2>/dev/null && echo "   ✅ Granted privileges on: $db"
    done
    
    psql postgres -c "ALTER USER realtorrajaram_user WITH SUPERUSER;" 2>/dev/null && echo "   ✅ Granted superuser privileges"
    
    echo ""
    echo "5. Setting user configurations..."
    psql postgres -c "ALTER ROLE realtorrajaram_user SET client_encoding TO 'utf8';" 2>/dev/null
    psql postgres -c "ALTER ROLE realtorrajaram_user SET default_transaction_isolation TO 'read committed';" 2>/dev/null
    psql postgres -c "ALTER ROLE realtorrajaram_user SET timezone TO 'UTC';" 2>/dev/null
    
    echo "   ✅ User configurations set"
else
    echo "   ❌ Failed to create user"
    echo "   Trying alternative method..."
    
    # Try with sudo
    sudo -u postgres psql -c "CREATE USER realtorrajaram_user WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✅ User created with sudo"
    else
        echo "   ❌ All methods failed"
        echo "   Please run these commands manually:"
        echo "   sudo -u postgres psql"
        echo "   Then in psql shell:"
        echo "   CREATE USER realtorrajaram_user WITH PASSWORD '$DB_PASSWORD';"
        echo "   ALTER USER realtorrajaram_user WITH SUPERUSER;"
    fi
fi

echo ""
echo "6. Testing connection..."
if psql -d realtorrajaram_prod -U realtorrajaram_user -c "SELECT '✅ Connection successful' AS message;" 2>/dev/null; then
    echo "   ✅ Database connection test PASSED"
else
    echo "   ⚠️  Connection test failed"
    echo "   Testing with different methods..."
    
    # Test with localhost
    psql -h localhost -d realtorrajaram_prod -U realtorrajaram_user -c "SELECT 1;" 2>/dev/null && echo "   ✅ Connected via localhost"
    
    # Test with postgres user
    psql -d realtorrajaram_prod -c "\dt" 2>/dev/null && echo "   ✅ Can connect as current user"
fi

echo ""
echo "7. Saving credentials..."
cat > ~/database_credentials.txt << CREDENTIALS
=== RAJA RAM REAL ESTATE DATABASE CREDENTIALS ===
Created: $(date)

DATABASES:
1. Production: realtorrajaram_prod
2. Development: realtorrajaram_dev  
3. Testing: realtorrajaram_test

USER CREDENTIALS:
Username: realtorrajaram_user
Password: $DB_PASSWORD
Host: localhost
Port: 5432

CONNECTION STRINGS:
For Django settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'realtorrajaram_prod',
        'USER': 'realtorrajaram_user',
        'PASSWORD': '$DB_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

PostgreSQL URL:
postgresql://realtorrajaram_user:$DB_PASSWORD@localhost:5432/realtorrajaram_prod

MANAGEMENT COMMANDS:
Start PostgreSQL: brew services start postgresql@14
Stop PostgreSQL: brew services stop postgresql@14
Backup: pg_dump -U realtorrajaram_user realtorrajaram_prod > backup.sql
Restore: psql -U realtorrajaram_user realtorrajaram_prod < backup.sql
CREDENTIALS

chmod 600 ~/database_credentials.txt
echo "   ✅ Credentials saved to: ~/database_credentials.txt"

echo ""
echo "8. Final verification..."
echo "   Listing databases:"
psql -l | grep realtorrajaram | while read line; do echo "   - $line"; done 2>/dev/null || echo "   ⚠️  Could not list databases"

echo ""
echo "=== SETUP COMPLETE ==="
echo ""
echo "To use with Django:"
echo "1. Update your .env file with:"
echo "   DB_NAME=realtorrajaram_prod"
echo "   DB_USER=realtorrajaram_user"
echo "   DB_PASSWORD=$DB_PASSWORD"
echo "   DB_HOST=localhost"
echo "   DB_PORT=5432"
echo ""
echo "2. Run migrations: python manage.py migrate"
echo "3. Create superuser: python manage.py createsuperuser"
echo ""
echo "For AWS Lightsail deployment, use the same credentials!"
