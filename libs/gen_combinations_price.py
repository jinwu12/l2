
#拉取全量组合
#https://trello.com/c/LCDudDre
def get_symbol_combinations(db,symbol_methods):
    #初始化db指针
    db_cursor = db.cursor()
    #拼接拉取sql并拉取组合数据
    sql = 'select id,combination_name,symbol_list,combined_method,combination_3point_price,trading_symbol from Global_Config.symbol_combinations'
    db_cursor.execute(sql)
    sql_result=db_cursor.fetchall()
    result_list = []
    #遍历结果
    for i in sql_result:
        id = int(i[0])
        combination_name = i[1] 
        symbol_list = str(i[2])
        combined_method = i[3]
        tri_point_price = int(i[4])
        trading_symbol = i[5]
        #判断combination_name是否为空，如果为空则根据symbol_list拉取symbol_name，与combined_method组成新的combination_name，然后update数据库中的combination_name
        if combination_name == '':
            for symbol_id in symbol_list.split(','):
                print(symbol_id,get_symbol_name_by_id(symbol_id,symbol_methods))
                combination_name = combination_name+get_symbol_name_by_id(symbol_id,symbol_methods)[0][1]+'-'
            combination_name = combination_name + combined_method
            #更新到db中
            sql = 'update Global_Config.symbol_combinations set combination_name='+combination_name+' where id='+id
            db_cursor.execute(sql)
            db.commit()
        #如果combination_3point_price为0，则运行calculate_combination_3point_price更新
        if tri_point_price == 0:
            tri_point_price = calculate_combination_3point_price(db,id)['tri_point_price']
        #拼接结果
        result = {}
        result['id'] = id
        result['combination_name'] = combination_name
        result['symbol_list'] = symbol_list
        result['combined_method'] = combined_method
        result['tri_point_price'] = tri_point_price
        result['trading_symbol'] = trading_symbol
        result_list.append(result)
    return result_list

    



#计算特定组合的3点价格
#如果更新了symbol_list中的组合，需要将combination_3point_price设置为0，然后重新运行此函数
#https://trello.com/c/yREdUOrk
def calculate_combination_3point_price(db,combinations_id):
    #初始化db指针
    db_cursor = db.cursor()
    #拼接拉取combinations_id对应的symbol_list及3点价格的sql
    sql = 'select  id,symbol_list,combination_3point_price from Global_Config.symbol_combinations where id='+str(combinations_id)
    #拉取数据并赋值
    db_cursor.execute(sql)
    sql_result=db_cursor.fetchall()
    id = int(sql_result[0][0])
    symbol_list = sql_result[0][1] 
    tri_point_price = sql_result[0][2]
    result={}
    
    #当combination_3point_price等于0时，证明该组合未曾生成过3点价格，则计算3点价格并更新到db中
    if tri_point_price == 0:
        tri_point_price = int(len(symbol_list.split(','))*3)
        sql = 'update Global_Config.symbol_combinations set combination_3point_price='+str(tri_point_price)+' where id='+str(id)
        db_cursor.execute(sql)
        db.commit()
    #当combination_3point_price不等于0时，证明该组合已产生过价格，直接返回即可
    result['id'] = id
    result['tri_point_price'] = tri_point_price
    return result
        



# 从Tbl_symbol_method表中拉取method_id对应的symbol name，供get_symbol_combinations中生成组合名称使用
def get_symbol_name_by_id(symbol_id, symbol_method_list):
    result = []
    for item in symbol_method_list:
        if item.get('method_id') == symbol_id:
            result.append((symbol_id, item.get('symbol_name')))
    return result
