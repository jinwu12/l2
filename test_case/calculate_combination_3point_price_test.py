import sys
sys.path.append('..')
from libs import commons
from libs import gen_combinations_price

test_db = commons.db_connect()
print(gen_combinations_price.calculate_combination_3point_price(test_db,1))

