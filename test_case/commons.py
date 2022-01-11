import sys
sys.path.append("..")
from libs import commons
from libs import get_historical_data

#连接db
test_db = commons.db_connect()
result = commons.get_all_symbol_attr(test_db)
for i in result:
    print(i)
    #print(i.get('method_id'), i.get('symbol_name'))
test_db.close()
