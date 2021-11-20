create table single_symbol_original_data_template(
symbol_name VARCHAR(16) NOT NULL comment '品类名称',
ts bigint(64) unsigned NOT NULL comment '时间点数据均需要转换为unix timestamp后再入库',
price_open DOUBLE NOT NULL comment '开盘价',
price_hgih DOUBLE NOT NULL comment '最高价',
price_low DOUBLE NOT NULL comment '最低价',
price_closed DOUBLE NOT NULL comment '收盘价',
comments TEXT comment '备注字段'
);
