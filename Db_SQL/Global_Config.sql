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
  PRIMARY KEY (`method_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tbl_symbol_method`
--

LOCK TABLES `Tbl_symbol_method` WRITE;
/*!40000 ALTER TABLE `Tbl_symbol_method` DISABLE KEYS */;
/*!40000 ALTER TABLE `Tbl_symbol_method` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_combinations_list`
--

LOCK TABLES `production_combinations_list` WRITE;
/*!40000 ALTER TABLE `production_combinations_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `production_combinations_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `production_symbol_list`
--

DROP TABLE IF EXISTS `production_symbol_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_symbol_list` (
  `symbol_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '交易品类ID',
  `symbol_name` varchar(16) NOT NULL COMMENT '交易品类名称',
  `contract_size` varchar(16) DEFAULT NULL COMMENT '合约数量，每手交易的数额，可以是交易单位或货币价格，如100oz或100000usd',
  `digits` tinyint unsigned NOT NULL COMMENT '小数点后位数',
  `3point_price` decimal(24,12) NOT NULL COMMENT '3点取值，最多到小数点后12位，包括小数点后最多支持总共24位数字',
  `comments` text COMMENT '备注字段',
  PRIMARY KEY (`symbol_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_symbol_list`
--

LOCK TABLES `production_symbol_list` WRITE;
/*!40000 ALTER TABLE `production_symbol_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `production_symbol_list` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_timezone_list`
--

LOCK TABLES `production_timezone_list` WRITE;
/*!40000 ALTER TABLE `production_timezone_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `production_timezone_list` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sim_combinations_list`
--

LOCK TABLES `sim_combinations_list` WRITE;
/*!40000 ALTER TABLE `sim_combinations_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `sim_combinations_list` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sim_symbol_list`
--

LOCK TABLES `sim_symbol_list` WRITE;
/*!40000 ALTER TABLE `sim_symbol_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `sim_symbol_list` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sim_timezone_list`
--

LOCK TABLES `sim_timezone_list` WRITE;
/*!40000 ALTER TABLE `sim_timezone_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `sim_timezone_list` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-11-21  3:02:50
