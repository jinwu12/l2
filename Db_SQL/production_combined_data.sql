-- MySQL dump 10.13  Distrib 8.0.27, for macos12.0 (arm64)
--
-- Host: db.weijianliao.com    Database: production_combined_data
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
-- Table structure for table `combined_symbol_original_data_template`
--

DROP TABLE IF EXISTS `combined_symbol_original_data_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `combined_symbol_original_data_template` (
  `symbol_name` varchar(256) DEFAULT NULL,
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  UNIQUE KEY `unique_ts_symbol_price` (`symbol_name`,`ts`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `daily_combined_data_template`
--

DROP TABLE IF EXISTS `daily_combined_data_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_combined_data_template` (
  `combination_id` int unsigned NOT NULL COMMENT '交易组合id，用于标识该日线行情记录表为哪个交易组合的数据',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `timezone_id` int unsigned NOT NULL COMMENT '时区id，用于标识该表使用的是哪个时区',
  `price_closed` double NOT NULL COMMENT '以该时区为准的日线收盘价',
  `is_recorded` tinyint(1) NOT NULL COMMENT '该价格是否需要在行情记录表中进行显性显示，0为小幅波动，不需要；1为需要',
  `recorded_column` tinyint unsigned NOT NULL COMMENT '当前记录栏。0：不记录；1：次级回升栏；2：自然回升栏；3：上升趋势栏；4：下降趋势栏；5：自然回撤栏；6：次级回撤栏',
  `is_pivot` tinyint(1) NOT NULL COMMENT '该点是否关键点,1为是,0为否',
  `comments` text COMMENT '备注字段'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-14  0:20:32
