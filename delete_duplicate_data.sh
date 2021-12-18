#!/bin/bash
echo 'show tables'|mysql original_data_source|grep -v Tables_in_original_data_source|while read table ;do echo "DELETE FROM $table WHERE id NOT IN ( SELECT dt.minno FROM (SELECT MIN(id) AS minno FROM $table GROUP BY ts ) dt )"|mysql original_data_source; done
