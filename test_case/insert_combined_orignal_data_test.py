import sys
sys.path.append('..')
from libs import gen_combinations_price, commons
test_db = commons.db_connect()

combination_symbol_tri_point_price = {
        'XAUUSD' : '3USD',
        'TNX' : 0.03,
        'DXY' : 0.3
        }


combination_price = ['XAUUSD-TNX-DXY', 1640973540, 301.25, 302.53, 300.11, 301.12]

combined_price = {
        'combination_id' : 1, 
        'symbol_3point_price' : combination_symbol_tri_point_price, 
        #or strict_match
        'combined_method' : 'best_effort_match', 
        'combination_3point_price' : 9,
        #or 1h
        'interval' : '1m', 
        'combination_price' : combination_price
        }

combined_price_list = [] 
combined_price_list.append(combined_price)

combination_price = ['XAUUSD-TNX-DXY_MT5', 1639354380, 301.25, 302.53, 300.11, 301.12]

combined_price = {
        'combination_id' : 2, 
        'symbol_3point_price' : combination_symbol_tri_point_price, 
        #or strict_match
        'combined_method' : 'best_effort_match', 
        'combination_3point_price' : 9,
        #or 1h
        'interval' : '1m', 
        'combination_price' : combination_price
        }

combined_price_list.append(combined_price)

#print(combined_price_list)
gen_combinations_price.insert_combined_orignal_data(test_db, combined_price_list)
