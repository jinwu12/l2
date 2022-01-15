import sys
sys.path.append('..')
from libs import commons
from libs import gen_combinations_price
import pdb

test_db = commons.db_connect()
symbol_methods=commons.get_all_symbol_attr(test_db)
print(gen_combinations_price.get_symbol_name_by_id(1,symbol_methods))
gen_combinations_price.get_symbol_combinations(test_db,symbol_methods)

