# 从Tbl_symbol_method表中拉取method_id对应的symbol name，供get_symbol_combinations中生成组合名称使用
def get_symbol_name_by_id(symbol_id, symbol_method_list):
    result = []
    for item in symbol_method_list:
        if item.get('method_id') == symbol_id:
            result.append((symbol_id, item.get('symbol_name')))
    return result
