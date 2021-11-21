
def get_symbol_method(db):
    #通过参数传入db连接
    symbol_method_db = db
    symbol_method_cursor = symbol_method_db.cursor()
    #获取全量symbol对应的method
    get_all_symbol_method = 'select distinct symbol_name,method_name from Global_Config.Tbl_symbol_method'
    resutl_list = symbol_method_cursor.execute(get_all_symbol_method)

    #返回结果列表
    return symbol_method_cursor



