#!/bin/bash

# 指定数据库名称和基础目录路径
DATABASE="surf"
# shellcheck disable=SC2046
BASE_DIR="$(dirname $(dirname $(realpath $0)))"
SQL_DIR="$BASE_DIR/sql"

# 执行新数据库初始化的 SQL 文件
echo "Executing $SQL_DIR/new_surf_sql.sql..."
sudo -u postgres psql -d "$DATABASE" -f "$SQL_DIR/new_surf_sql.sql"
if [ $? -ne 0 ]; then
    echo "Error executing new_surf_sql.sql"
else
    echo "database init executed successfully"
fi

# 遍历并执行 tables 目录中的所有 .sql 文件
TABLES_DIR="$SQL_DIR/tables"

if [ ! -d "$TABLES_DIR" ]; then
    echo "Directory $TABLES_DIR does not exist."
    exit 1
fi

for file in "$TABLES_DIR"/*.sql; do
    if [ -f "$file" ]; then
        echo "Executing $file..."
        sudo -u postgres psql -d "$DATABASE" -f "$file"
        if [ $? -ne 0 ]; then
            echo "Error executing $file"
        else
            echo "$file executed successfully."
        fi
    fi
done
