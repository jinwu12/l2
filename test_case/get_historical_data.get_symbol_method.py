import sys
sys.path.append("..")
from libs import commons
from libs import get_historical_data

#连接db
test_db = commons.db_connect()
result = get_historical_data.get_symbol_method(test_db)
for i in result:
    print(i[0],i[1])
test_db.close()
