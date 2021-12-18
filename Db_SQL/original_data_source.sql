-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: localhost    Database: original_data_source
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
-- Table structure for table `DXY_1h_original_data_202112`
--

DROP TABLE IF EXISTS `DXY_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DXY_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11966 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DXY_1m_original_data_202112`
--

DROP TABLE IF EXISTS `DXY_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DXY_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59597 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DXY_MT5_1h_original_data_202112`
--

DROP TABLE IF EXISTS `DXY_MT5_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DXY_MT5_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DXY_MT5_1m_original_data_202112`
--

DROP TABLE IF EXISTS `DXY_MT5_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DXY_MT5_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  UNIQUE KEY `unique_ts_symbol_price` (`symbol_name`,`ts`),
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19347 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `EURUSD_1h_original_data_202112`
--

DROP TABLE IF EXISTS `EURUSD_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EURUSD_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=263 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `EURUSD_1m_original_data_202112`
--

DROP TABLE IF EXISTS `EURUSD_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EURUSD_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36532 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `GBPUSD_1h_original_data_202112`
--

DROP TABLE IF EXISTS `GBPUSD_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GBPUSD_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=263 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `GBPUSD_1m_original_data_202112`
--

DROP TABLE IF EXISTS `GBPUSD_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GBPUSD_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36537 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TNX_1h_original_data_202112`
--

DROP TABLE IF EXISTS `TNX_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TNX_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3490 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TNX_1m_original_data_202112`
--

DROP TABLE IF EXISTS `TNX_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TNX_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17558 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDCAD_1h_original_data_202112`
--

DROP TABLE IF EXISTS `USDCAD_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDCAD_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=262 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDCAD_1m_original_data_202112`
--

DROP TABLE IF EXISTS `USDCAD_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDCAD_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36559 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDCHF_1h_original_data_202112`
--

DROP TABLE IF EXISTS `USDCHF_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDCHF_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDCHF_1m_original_data_202112`
--

DROP TABLE IF EXISTS `USDCHF_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDCHF_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36264 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDJPY_1h_original_data_202112`
--

DROP TABLE IF EXISTS `USDJPY_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDJPY_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=263 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDJPY_1m_original_data_202112`
--

DROP TABLE IF EXISTS `USDJPY_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDJPY_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36509 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDSEK_1h_original_data_202112`
--

DROP TABLE IF EXISTS `USDSEK_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDSEK_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USDSEK_1m_original_data_202112`
--

DROP TABLE IF EXISTS `USDSEK_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USDSEK_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36172 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `XAUUSD_1h_original_data_202112`
--

DROP TABLE IF EXISTS `XAUUSD_1h_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `XAUUSD_1h_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11652 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `XAUUSD_1m_original_data_202112`
--

DROP TABLE IF EXISTS `XAUUSD_1m_original_data_202112`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `XAUUSD_1m_original_data_202112` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
  `ts` bigint unsigned NOT NULL COMMENT '时间点数据均需要转换为unix timestamp后再入库',
  `price_open` double NOT NULL COMMENT '开盘价',
  `price_hgih` double NOT NULL COMMENT '最高价',
  `price_low` double NOT NULL COMMENT '最低价',
  `price_closed` double NOT NULL COMMENT '收盘价',
  `comments` text COMMENT '备注字段',
  `id` bigint NOT NULL AUTO_INCREMENT,
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=62150 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `single_symbol_original_data_template`
--

DROP TABLE IF EXISTS `single_symbol_original_data_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `single_symbol_original_data_template` (
  `symbol_name` varchar(16) NOT NULL COMMENT '品类名称',
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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-18  3:28:13
