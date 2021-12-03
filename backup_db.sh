#!/bin/bash
cat db_list.txt|while read db;do
mysqldump -d $db > ./Db_SQL/$db.sql
done
