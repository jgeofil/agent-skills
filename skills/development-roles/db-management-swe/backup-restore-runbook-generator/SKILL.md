---
name: backup-restore-runbook-generator
description: >-
  Creates comprehensive disaster recovery procedures with automated backup scripts, restore procedures, validation checks, and role assignments. Use for "database backup", "disaster recovery", "data restore", or "DR planning".
license: MIT
metadata:
  version: "1.0"
  category: db-management-swe
---

# Backup/Restore Runbook Generator

Create reliable disaster recovery procedures for your databases.

## Backup Strategy

````markdown
# Database Backup Strategy

## Backup Types

### 1. Full Backup (Daily)

- **When**: 2:00 AM UTC
- **Retention**: 30 days
- **Storage**: S3 `s3://backups/full/`
- **Size**: ~50 GB
- **Duration**: ~45 minutes

### 2. Incremental Backup (Hourly)

- **When**: Every hour
- **Retention**: 7 days
- **Storage**: S3 `s3://backups/incremental/`
- **Size**: ~500 MB
- **Duration**: ~5 minutes

### 3. Transaction Log Backup (Every 15 min)

- **When**: Every 15 minutes
- **Retention**: 3 days
- **Storage**: S3 `s3://backups/wal/`
- **Point-in-time recovery capability**

## Backup Automation

### PostgreSQL

```bash
#!/bin/bash
# scripts/backup-postgres.sh

set -e

# Configuration
DB_NAME="production"
DB_USER="postgres"
DB_HOST="postgres.example.com"
BACKUP_DIR="/var/backups/postgres"
S3_BUCKET="s3://my-backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="${DB_NAME}_${DATE}.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🔄 Starting backup: $FILENAME"

# Full backup with pg_dump
pg_dump \
  --host=$DB_HOST \
  --username=$DB_USER \
  --dbname=$DB_NAME \
  --format=custom \
  --compress=9 \
  --file=$BACKUP_DIR/$FILENAME \
  --verbose

# Verify backup
if [ -f "$BACKUP_DIR/$FILENAME" ]; then
  SIZE=$(du -h "$BACKUP_DIR/$FILENAME" | cut -f1)
  echo "✅ Backup created: $SIZE"
else
  echo "❌ Backup failed"
  exit 1
fi

# Upload to S3
echo "📤 Uploading to S3..."
aws s3 cp $BACKUP_DIR/$FILENAME $S3_BUCKET/ \
  --storage-class STANDARD_IA

# Verify upload
if aws s3 ls $S3_BUCKET/$FILENAME; then
  echo "✅ Uploaded to S3"
else
  echo "❌ S3 upload failed"
  exit 1
fi

# Cleanup old local backups (keep last 7 days)
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete
echo "🗑️  Cleaned up old local backups"

# Send notification
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"✅ Database backup complete: $FILENAME ($SIZE)\"}"

echo "✅ Backup complete!"
```
````

### MySQL

```bash
#!/bin/bash
# scripts/backup-mysql.sh

set -e

DB_NAME="production"
DB_USER="root"
DB_PASSWORD=$MYSQL_PASSWORD
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="${DB_NAME}_${DATE}.sql.gz"

echo "🔄 Starting MySQL backup..."

# Backup with mysqldump
mysqldump \
  --user=$DB_USER \
  --password=$DB_PASSWORD \
  --single-transaction \
  --quick \
  --lock-tables=false \
  --databases $DB_NAME \
  | gzip > /var/backups/mysql/$FILENAME

# Upload to S3
aws s3 cp /var/backups/mysql/$FILENAME s3://my-backups/mysql/

echo "✅ Backup complete!"
```

## Best Practices

1. **Test restores regularly**: Quarterly DR drills
2. **Automate backups**: Never rely on manual processes
3. **Multiple locations**: Cross-region backup storage
4. **Monitor backup health**: Alert on failures
5. **Document procedures**: Keep runbook updated
6. **Encrypt backups**: Protect sensitive data
7. **Version control**: Track backup script changes

## Output Checklist

- [ ] Backup automation scripts
- [ ] Restore procedures documented
- [ ] Validation checks defined
- [ ] PITR procedure (if applicable)
- [ ] DR runbook created
- [ ] Role assignments documented
- [ ] RTO/RPO defined
- [ ] Backup monitoring configured


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

