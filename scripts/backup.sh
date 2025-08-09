#!/bin/bash
set -e

# Backup script for AGENT project

# Check for help flag
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    cat << 'EOF'
Usage: backup.sh [OPTIONS]

Create a backup of the AGENT project

Options:
  --help, -h    Show this help message

Description:
  This script creates a backup of the AGENT project including:
  - Source code (agent/, rust/)
  - Documentation (docs/)
  - Scripts (scripts/)
  - Configuration files
  - Compiled libraries (if present)

Examples:
  ./scripts/backup.sh
EOF
    exit 0
fi

echo "💾 Creating AGENT project backup..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Create backup directory with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups/agent_backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "📁 Backup location: $BACKUP_DIR"

# Backup source code
echo "📋 Backing up source code..."
cp -r agent/ "$BACKUP_DIR/"
cp -r rust/ "$BACKUP_DIR/"
cp -r docs/ "$BACKUP_DIR/"
cp -r scripts/ "$BACKUP_DIR/"

# Backup configuration files
echo "📋 Backing up configuration..."
cp *.md "$BACKUP_DIR/" 2>/dev/null || true
cp *.json "$BACKUP_DIR/" 2>/dev/null || true
cp *.txt "$BACKUP_DIR/" 2>/dev/null || true
cp *.toml "$BACKUP_DIR/" 2>/dev/null || true

# Backup compiled libraries (if they exist)
if [ -d "lib" ]; then
    echo "📋 Backing up compiled libraries..."
    cp -r lib/ "$BACKUP_DIR/"
fi

# Create backup manifest
echo "📋 Creating backup manifest..."
cat > "$BACKUP_DIR/BACKUP_MANIFEST.md" << EOF
# AGENT Project Backup

**Backup Date**: $(date)
**Timestamp**: $TIMESTAMP
**Backup Size**: $(du -sh "$BACKUP_DIR" | cut -f1)

## Contents
- Source code (agent/, rust/)
- Documentation (docs/)
- Scripts (scripts/)
- Configuration files
- Compiled libraries (if present)

## Restore Instructions
1. Extract backup to desired location
2. Run: \`./scripts/build_rust.sh\` to rebuild Rust components
3. Run: \`./scripts/test_integration.sh\` to verify functionality

## System Info
- Host: $(hostname)
- User: $(whoami)
- Python: $(python3 --version)
- Rust: $(rustc --version 2>/dev/null || echo "Not available")
EOF

# Compress backup (optional)
if command -v tar >/dev/null 2>&1; then
    echo "🗜️  Compressing backup..."
    cd backups
    tar -czf "agent_backup_$TIMESTAMP.tar.gz" "agent_backup_$TIMESTAMP/"
    rm -rf "agent_backup_$TIMESTAMP/"
    cd ..
    echo "✅ Compressed backup created: backups/agent_backup_$TIMESTAMP.tar.gz"
else
    echo "✅ Backup created: $BACKUP_DIR"
fi

# Cleanup old backups (keep last 5)
if [ -d "backups" ]; then
    echo "🧹 Cleaning up old backups (keeping last 5)..."
    cd backups
    ls -t agent_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    ls -t -d agent_backup_*/ 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null || true
    cd ..
fi

echo "🎉 Backup completed successfully!"
