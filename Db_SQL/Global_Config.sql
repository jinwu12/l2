-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: localhost    Database: Global_Config
-- ------------------------------------------------------
-- Server version	8.0.27-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Tbl_symbol_method`
--

DROP TABLE IF EXISTS `Tbl_symbol_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tbl_symbol_method` (
  `method_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `method_name` varchar(128) NOT NULL COMMENT '获取该symbol的函数名称',
  `comments` text COMMENT '备注字段',
  `timezone` varchar(128) NOT NULL COMMENT '该symbol从该数据源拉取时所在的时区，用于计算时间戳',
  `symbol_value` varchar(16) NOT NULL COMMENT '用于具体拉取该symbol数据时的标准化名称',
  `contract_size` varchar(32) DEFAULT NULL COMMENT '合约大小，外汇对为100000usd，xauusd为100oz；其余交易品类按照spec来设置',
  `digits` tinyint DEFAULT NULL COMMENT '该交易品类保留的小数位，由品类spec决定',
  `3point_price` decimal(12,10) DEFAULT NULL COMMENT '该symbol的3点取值，人为设置调整',
  PRIMARY KEY (`method_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account_info`
--

DROP TABLE IF EXISTS `account_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_info` (
  `account_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '账号唯一ID',
  `account_name` varchar(128) NOT NULL COMMENT '账号登陆名称',
  `account_platform` varchar(64) NOT NULL COMMENT '账号所属平台',
  `account_server` varchar(128) NOT NULL COMMENT '账号所在服务器',
  `account_pass` varchar(128) NOT NULL COMMENT '账号登陆密码',
  `desciption` text COMMENT '账号描述',
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `production_combinations_list`
--

DROP TABLE IF EXISTS `production_combinations_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_combinations_list` (
  `combination_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '交易组合ID',
  `combination_name` varchar(128) NOT NULL COMMENT '交易组合名称',
  `symbol_list` varchar(256) NOT NULL COMMENT '品类组合列表，交易品类id组合，以半角逗号分隔',
  `trading_symbol` varchar(256) NOT NULL COMMENT '实际进行交易的品类id列表，ALL为全部均可进行交易；多个交易品类以半角逗号分割；',
  `comments` text COMMENT '备注字段',
  PRIMARY KEY (`combination_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `production_timezone_list`
--

DROP TABLE IF EXISTS `production_timezone_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_timezone_list` (
  `time_zone_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '时区ID',
  `time_zone_name` varchar(32) NOT NULL COMMENT '时区名称',
  `time_zone` varchar(32) NOT NULL COMMENT '以UTC为准的时区，如UTC +3或UTC -5)',
  PRIMARY KEY (`time_zone_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sim_combinations_list`
--

DROP TABLE IF EXISTS `sim_combinations_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sim_combinations_list` (
  `combination_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '交易组合ID',
  `combination_name` varchar(128) NOT NULL COMMENT '交易组合名称',
  `symbol_list` varchar(256) NOT NULL COMMENT '品类组合列表，交易品类id组合，以半角逗号分隔',
  `trading_symbol` varchar(256) NOT NULL COMMENT '实际进行交易的品类id列表，ALL为全部均可进行交易；多个交易品类以半角逗号分割；',
  `comments` text COMMENT '备注字段',
  PRIMARY KEY (`combination_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sim_symbol_list`
--

DROP TABLE IF EXISTS `sim_symbol_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sim_symbol_list` (
  `symbol_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '交易品类ID',
  `symbol_name` varchar(16) NOT NULL COMMENT '交易品类名称',
  `contract_size` varchar(16) DEFAULT NULL COMMENT '合约数量，每手交易的数额，可以是交易单位或货币价格，如100oz或100000usd',
  `digits` tinyint unsigned NOT NULL COMMENT '小数点后位数',
  `3point_price` decimal(24,12) NOT NULL COMMENT '3点取值，最多到小数点后12位，包括小数点后最多支持总共24位数字',
  `comments` text COMMENT '备注字段',
  PRIMARY KEY (`symbol_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sim_timezone_list`
--

DROP TABLE IF EXISTS `sim_timezone_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sim_timezone_list` (
  `time_zone_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '时区ID',
  `time_zone_name` varchar(32) NOT NULL COMMENT '时区名称',
  `time_zone` varchar(32) NOT NULL COMMENT '以UTC为准的时区，如UTC +3或UTC -5)',
  PRIMARY KEY (`time_zone_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `symbol_combinations`
--

DROP TABLE IF EXISTS `symbol_combinations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `symbol_combinations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `combination_name` varchar(256) DEFAULT NULL COMMENT '组合名称，默认为空。当为空时通过symbol list中的symbol组合来生成',
  `symbol_list` varchar(128) NOT NULL COMMENT '组合价格的symbol列表，半角逗号分隔',
  `combined_method` varchar(64) NOT NULL COMMENT '组合价格匹配方式，strict_match或者best_effort_match',
  `combination_3point_price` int NOT NULL DEFAULT '0' COMMENT '组合价格3点取值，默认为0（即为symbol数量*3）',
  `comments` text COMMENT '备注字段',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-31 15:35:23
