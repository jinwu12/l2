create table sim_symbol_list(
symbol_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT comment '交易品类ID',
symbol_name VARCHAR(16) NOT NULL comment '交易品类名称',
contract_size VARCHAR(16) comment '合约数量，每手交易的数额，可以是交易单位或货币价格，如100oz或100000usd',
digits TINYINT UNSIGNED NOT NULL comment '小数点后位数',
3point_price DECIMAL(24,12) NOT NULL  comment '3点取值，最多到小数点后12位，包括小数点后最多支持总共24位数字',
comments TEXT comment '备注字段'
);


create table sim_combinations_list(
combination_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT comment '交易组合ID',
combination_name VARCHAR(128) NOT NULL  comment '交易组合名称',
symbol_list VARCHAR(256) NOT NULL comment '品类组合列表，交易品类id组合，以半角逗号分隔',
trading_symbol VARCHAR(256) NOT NULL comment '实际进行交易的品类id列表，ALL为全部均可进行交易；多个交易品类以半角逗号分割；',
comments TEXT COMMENT '备注字段'
);

create table sim_timezone_list(
time_zone_id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT comment '时区ID',
time_zone_name varchar(32) NOT NULL comment '时区名称',
time_zone VARCHAR(32) NOT NULL comment '以UTC为准的时区，如UTC +3或UTC -5)'
);
