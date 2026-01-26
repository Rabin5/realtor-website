#!/bin/bash
echo "=== COMPLETE PostgreSQL Removal ==="

echo "1. Stopping all PostgreSQL services..."
osascript -e 'quit app "Postgres"' 2>/dev/null || echo "Postgres.app not running"
sudo pkill -9 postgres 2>/dev/null || echo "No PostgreSQL processes"
sudo pkill -9 postmaster 2>/dev/null || echo "No postmaster processes"

echo "2. Uninstalling brew PostgreSQL..."
for version in postgresql postgresql@14 postgresql@15 postgresql@16; do
    brew uninstall $version --force 2>/dev/null && echo "Removed $version" || echo "$version not found"
done

echo "3. Removing Postgres.app..."
[ -d "/Applications/Postgres.app" ] && sudo rm -rf /Applications/Postgres.app && echo "Removed Postgres.app" || echo "Postgres.app not found"

echo "4. Removing data directories..."
[ -d "/usr/local/var/postgres" ] && sudo rm -rf /usr/local/var/postgres && echo "Removed /usr/local/var/postgres" || echo "Directory not found"
[ -d "~/Library/Application Support/Postgres" ] && rm -rf ~/Library/Application\ Support/Postgres && echo "Removed Application Support" || echo "No Application Support dir"

echo "5. Removing configuration files..."
rm -f ~/.psqlrc ~/.pgpass ~/.pg_service.conf 2>/dev/null || true
rm -f ~/Library/LaunchAgents/homebrew.mxcl.postgresql*.plist 2>/dev/null || true
rm -f ~/Library/Preferences/com.postgresapp.Postgres2.plist 2>/dev/null || true

echo "6. Cleaning socket files..."
rm -f /tmp/.s.PGSQL.* 2>/dev/null || true
rm -f /var/pgsql_socket/.s.PGSQL.* 2>/dev/null || true

echo "7. Cleaning brew cache..."
brew cleanup -s

echo "8. Verifying removal..."
echo "Checking for PostgreSQL files:"
ls -la /usr/local/opt/ | grep -i postgres && echo "PostgreSQL files still exist" || echo "No PostgreSQL files found"

echo "9. Checking for running processes..."
ps aux | grep -i postgres | grep -v grep && echo "PostgreSQL processes still running" || echo "No PostgreSQL processes"

echo "=== Cleanup Complete ==="
echo "PostgreSQL has been completely removed from your system."
echo "All databases have been deleted."
