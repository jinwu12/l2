create table single_symbol_original_data_template(
symbol_name varchar(32) not null '单个品类名称',
timestamp bigint not null PRIMARY KEY '时间点，所有粒度数据均需要转换为unix timestamp后再入库',
open float not null '开盘价',
high float not null '最高价',
low float  not null '最低价',
closed float not null '收盘价',
comment text default null
);
 