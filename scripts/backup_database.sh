#!/bin/bash
# Can be installed into your crontab, eg. Run daily at midnight system time:
# 0 0 * * * /opt/saltyboy/scripts/backup_database.sh -d /home/<user>/postgres_db_backup -u postgres -c saltyboy_postgres_1 -r 10

DUMP_DIR=postgres_dumps
POSTGRES_USER=postgres
CONTAINER=saltyboy_postgres_1
RETAIN_DAYS=10


usage () {
    echo "Usage: $0 [-d <dump path>] [-u <postgres user>] [-c <container name>] [-n <number of days of backups to retain>] [-h]"
    echo "Generates a database dump."
    echo "NOTE: Requires gzip to be installed"
    echo ""
    echo "-d    Path to dump the dump to. Defaults to: $DUMP_DIR."
    echo "-u    Postgres user to connect with. Defaults to: $POSTGRES_USER."
    echo "-c    Docker container to pull database dump from. Defaults to: $CONTAINER."
    echo "-r    Number of days of dumps to retain. Defaults to: $RETAIN_DAYS."
    echo "-h    Display this help message and exit."
}

while getopts "d:u:c:r:h" name; do
    case $name in
        d) DUMP_DIR="$OPTARG";;
        u) POSTGRES_USER="$OPTARG";;
        c) CONTAINER="$OPTARG";;
        r) RETAIN_DAYS="$OPTARG";;
        h) usage && exit 0;;
        *) usage && exit 2;;
    esac
done

set -e

DUMP_DATE=$(date "+%Y-%m-%d_%H_%M_%S")
DUMP_PATH="$DUMP_DIR/$DUMP_DATE.sql.gz"
echo "Dumping database to: $DUMP_PATH"
echo "Using Postgres user: $POSTGRES_USER"
echo "Using Docker container: $CONTAINER"

docker exec -t "$CONTAINER" pg_dumpall -c -U "$POSTGRES_USER" | gzip > "$DUMP_PATH"
find "$DUMP_PATH" -maxdepth 1 -name "*.sql.gz" -type f -mtime +"$RETAIN_DAYS" -delete