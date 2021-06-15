-- MySQL dump 10.13  Distrib 8.0.21, for Linux (x86_64)
--
-- Host: localhost    Database: lopos_test
-- ------------------------------------------------------
-- Server version	8.0.21-0ubuntu0.20.04.4

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
-- Table structure for table `anchor`
--

DROP TABLE IF EXISTS `anchor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `anchor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `addr` int NOT NULL,
  `group` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `addrid_UNIQUE` (`addr`),
  KEY `fk_anchor_1_idx` (`addr`),
  CONSTRAINT `fk_anchor_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cell`
--

DROP TABLE IF EXISTS `cell`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cell` (
  `core` int NOT NULL,
  `edge` int NOT NULL,
  PRIMARY KEY (`core`,`edge`),
  KEY `index1` (`core`),
  KEY `fk_cell_2_idx` (`edge`),
  CONSTRAINT `fk_cell_1` FOREIGN KEY (`core`) REFERENCES `anchor` (`id`),
  CONSTRAINT `fk_cell_2` FOREIGN KEY (`edge`) REFERENCES `anchor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cir`
--

DROP TABLE IF EXISTS `cir`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cir` (
  `reporter` int NOT NULL,
  `dev` int NOT NULL,
  `asn` int NOT NULL DEFAULT '0',
  `rxQual` float(6,3) DEFAULT NULL,
  `fpPow` float(6,3) DEFAULT NULL,
  `rxPow` float(6,3) DEFAULT NULL,
  `cir0` int DEFAULT NULL,
  `cir1` int DEFAULT NULL,
  `cir2` int DEFAULT NULL,
  `cir3` int DEFAULT NULL,
  `cir4` int DEFAULT NULL,
  `cir5` int DEFAULT NULL,
  `cir6` int DEFAULT NULL,
  `cir7` int DEFAULT NULL,
  `cir8` int DEFAULT NULL,
  `cir9` int DEFAULT NULL,
  `cir10` int DEFAULT NULL,
  `cir11` int DEFAULT NULL,
  `cir12` int DEFAULT NULL,
  `cir13` int DEFAULT NULL,
  `cir14` int DEFAULT NULL,
  `cir15` int DEFAULT NULL,
  `cir16` int DEFAULT NULL,
  `cir17` int DEFAULT NULL,
  `cir18` int DEFAULT NULL,
  `cir19` int DEFAULT NULL,
  `cir20` int DEFAULT NULL,
  `cir21` int DEFAULT NULL,
  `cir22` int DEFAULT NULL,
  `cir23` int DEFAULT NULL,
  `cir24` int DEFAULT NULL,
  `cir25` int DEFAULT NULL,
  `cir26` int DEFAULT NULL,
  `cir27` int DEFAULT NULL,
  `cir28` int DEFAULT NULL,
  `cir29` int DEFAULT NULL,
  `cir30` int DEFAULT NULL,
  `cir31` int DEFAULT NULL,
  `cir32` int DEFAULT NULL,
  `cir33` int DEFAULT NULL,
  `cir34` int DEFAULT NULL,
  `cir35` int DEFAULT NULL,
  `cir36` int DEFAULT NULL,
  `cir37` int DEFAULT NULL,
  `cir38` int DEFAULT NULL,
  `cir39` int DEFAULT NULL,
  `cir40` int DEFAULT NULL,
  `cir41` int DEFAULT NULL,
  `cir42` int DEFAULT NULL,
  `cir43` int DEFAULT NULL,
  `cir44` int DEFAULT NULL,
  `cir45` int DEFAULT NULL,
  `cir46` int DEFAULT NULL,
  `cir47` int DEFAULT NULL,
  `cir48` int DEFAULT NULL,
  `cir49` int DEFAULT NULL,
  `cir50` int DEFAULT NULL,
  `cir51` int DEFAULT NULL,
  `cir52` int DEFAULT NULL,
  `cir53` int DEFAULT NULL,
  `cir54` int DEFAULT NULL,
  `cir55` int DEFAULT NULL,
  `cir56` int DEFAULT NULL,
  `cir57` int DEFAULT NULL,
  `cir58` int DEFAULT NULL,
  `cir59` int DEFAULT NULL,
  `cir60` int DEFAULT NULL,
  `cir61` int DEFAULT NULL,
  `cir62` int DEFAULT NULL,
  `cir63` int DEFAULT NULL,
  `cir64` int DEFAULT NULL,
  `cir65` int DEFAULT NULL,
  `cir66` int DEFAULT NULL,
  `cir67` int DEFAULT NULL,
  `cir68` int DEFAULT NULL,
  `cir69` int DEFAULT NULL,
  `cir70` int DEFAULT NULL,
  `cir71` int DEFAULT NULL,
  `cir72` int DEFAULT NULL,
  `cir73` int DEFAULT NULL,
  `cir74` int DEFAULT NULL,
  `cir75` int DEFAULT NULL,
  `cir76` int DEFAULT NULL,
  `cir77` int DEFAULT NULL,
  `cir78` int DEFAULT NULL,
  `cir79` int DEFAULT NULL,
  `cir80` int DEFAULT NULL,
  `cir81` int DEFAULT NULL,
  `cir82` int DEFAULT NULL,
  `cir83` int DEFAULT NULL,
  `cir84` int DEFAULT NULL,
  `cir85` int DEFAULT NULL,
  `cir86` int DEFAULT NULL,
  `cir87` int DEFAULT NULL,
  `cir88` int DEFAULT NULL,
  `cir89` int DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`reporter`,`asn`),
  KEY `fk_cir_2_idx` (`updated`),
  KEY `fk_cir_2` (`dev`),
  CONSTRAINT `fk_cir_1` FOREIGN KEY (`reporter`) REFERENCES `device` (`addr`),
  CONSTRAINT `fk_cir_2` FOREIGN KEY (`dev`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device` (
  `addr` int NOT NULL AUTO_INCREMENT,
  `mac` varchar(18) NOT NULL,
  `vbattATdfu` float(4,3) DEFAULT NULL,
  `added` timestamp(3) NULL DEFAULT CURRENT_TIMESTAMP(3),
  `uwbTxPower` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`addr`),
  UNIQUE KEY `addr_UNIQUE` (`addr`),
  UNIQUE KEY `mac_UNIQUE` (`mac`),
  KEY `mac` (`mac`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dfu`
--

DROP TABLE IF EXISTS `dfu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dfu` (
  `addr` int NOT NULL,
  `dfuStat` int DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `version` int DEFAULT NULL,
  PRIMARY KEY (`addr`,`updated`),
  KEY `index2` (`addr`,`updated`),
  KEY `fk_dfu_2_idx` (`version`),
  CONSTRAINT `fk_dfu_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`),
  CONSTRAINT `fk_dfu_2` FOREIGN KEY (`version`) REFERENCES `version` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `map`
--

DROP TABLE IF EXISTS `map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `map` (
  `id` int NOT NULL AUTO_INCREMENT,
  `x1` int DEFAULT NULL,
  `y1` int DEFAULT NULL,
  `x2` int DEFAULT NULL,
  `y2` int DEFAULT NULL,
  `mapcol` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `motion`
--

DROP TABLE IF EXISTS `motion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `motion` (
  `addr` int NOT NULL,
  `asn` int DEFAULT NULL,
  `idx` int DEFAULT NULL,
  `x` int DEFAULT NULL,
  `y` int DEFAULT NULL,
  `z` int DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`addr`,`updated`),
  KEY `speedup` (`updated` DESC,`addr`),
  CONSTRAINT `fk_motion_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `plan`
--

DROP TABLE IF EXISTS `plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plan` (
  `addr` int NOT NULL,
  `scenario` int NOT NULL,
  `interval` int DEFAULT NULL,
  PRIMARY KEY (`addr`,`scenario`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `position`
--

DROP TABLE IF EXISTS `position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `position` (
  `addr` int NOT NULL,
  `asn` int NOT NULL DEFAULT '0',
  `x` int DEFAULT NULL,
  `y` int DEFAULT NULL,
  `z` int DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `numHyperbola` int DEFAULT NULL,
  `numPyTime` int DEFAULT NULL,
  PRIMARY KEY (`addr`,`updated`),
  KEY `pos_addr_upd` (`updated` DESC,`addr`),
  KEY `pos_addr` (`addr`),
  CONSTRAINT `fk_position_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stat`
--

DROP TABLE IF EXISTS `stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stat` (
  `addr` int NOT NULL,
  `asn` int NOT NULL DEFAULT '0',
  `version` int NOT NULL DEFAULT '0',
  `mac` varchar(17) DEFAULT NULL,
  `vbattRatio` int NOT NULL DEFAULT '0',
  `drift` int NOT NULL DEFAULT '0',
  `beaconRSSI` int NOT NULL DEFAULT '0',
  `devRSSI` int NOT NULL DEFAULT '0',
  `beaconRatio` int NOT NULL DEFAULT '0',
  `sgTxRatio` int NOT NULL DEFAULT '0',
  `sgRxRatio` int NOT NULL DEFAULT '0',
  `uwbTxRatio` int NOT NULL DEFAULT '0',
  `uwbRxRatio` int NOT NULL DEFAULT '0',
  `uwbTxPwr` int DEFAULT '0',
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`addr`,`updated`),
  KEY `speedup` (`updated` DESC,`addr`),
  CONSTRAINT `fk_stat_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys`
--

DROP TABLE IF EXISTS `sys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sys` (
  `installDate` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `beaconID` bit(8) NOT NULL,
  `SFmax` int NOT NULL,
  `SFticks` int NOT NULL,
  PRIMARY KEY (`installDate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag` (
  `id` int NOT NULL AUTO_INCREMENT,
  `addr` int NOT NULL,
  `group` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `addr_UNIQUE` (`addr`),
  KEY `fk_tag_1_idx` (`addr`),
  CONSTRAINT `fk_tag_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tdoa`
--

DROP TABLE IF EXISTS `tdoa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tdoa` (
  `edge` int NOT NULL,
  `sync` int NOT NULL,
  `tag` int NOT NULL,
  `asn` int NOT NULL DEFAULT '0',
  `ts` int DEFAULT '0',
  `drift` int DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`edge`,`sync`,`tag`,`asn`),
  KEY `fk_tdoa_2_idx` (`sync`),
  KEY `fk_tdoa_3_idx` (`tag`),
  KEY `speedup` (`updated` DESC,`tag`),
  CONSTRAINT `fk_tdoa_1` FOREIGN KEY (`edge`) REFERENCES `anchor` (`id`),
  CONSTRAINT `fk_tdoa_2` FOREIGN KEY (`sync`) REFERENCES `anchor` (`id`),
  CONSTRAINT `fk_tdoa_3` FOREIGN KEY (`tag`) REFERENCES `tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `timeInfo`
--

DROP TABLE IF EXISTS `timeInfo`;
/*!50001 DROP VIEW IF EXISTS `timeInfo`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `timeInfo` AS SELECT 
 1 AS `lastInsert`,
 1 AS `firstInsert`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `todo`
--

DROP TABLE IF EXISTS `todo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `todo` (
  `addr` int NOT NULL DEFAULT '0',
  `scheduleAT` int NOT NULL DEFAULT '0',
  `scenario` int DEFAULT '0',
  `actor` int DEFAULT '0',
  `rescheduleSF` int DEFAULT '0',
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`addr`,`scheduleAT`),
  KEY `time` (`updated`),
  KEY `device` (`addr`,`scheduleAT`),
  KEY `recent_schedule_device` (`addr`,`updated`,`scheduleAT`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `twr`
--

DROP TABLE IF EXISTS `twr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `twr` (
  `devA` int NOT NULL,
  `devB` int NOT NULL,
  `asn` int NOT NULL DEFAULT '0',
  `dist` int DEFAULT '0',
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`devA`,`devB`,`asn`),
  KEY `fk_twr_2_idx` (`devB`),
  CONSTRAINT `fk_twr_1` FOREIGN KEY (`devA`) REFERENCES `device` (`addr`),
  CONSTRAINT `fk_twr_2` FOREIGN KEY (`devB`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uwbstat`
--

DROP TABLE IF EXISTS `uwbstat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uwbstat` (
  `devTx` int NOT NULL,
  `devRx` int NOT NULL,
  `asn` int NOT NULL DEFAULT '0',
  `rxQual` float(6,3) DEFAULT NULL,
  `fpPow` float(6,3) DEFAULT NULL,
  `rxPow` float(6,3) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`devTx`,`devRx`,`asn`),
  KEY `fk_uwbstat_2_idx` (`devRx`),
  KEY `speedup` (`updated` DESC,`devTx`),
  KEY `uwbstat_devRx` (`devRx`),
  KEY `uwbstat_devTx` (`devTx`),
  KEY `uwbstat_upd_desc` (`updated`),
  CONSTRAINT `fk_uwbstat_1` FOREIGN KEY (`devTx`) REFERENCES `device` (`addr`),
  CONSTRAINT `fk_uwbstat_2` FOREIGN KEY (`devRx`) REFERENCES `device` (`addr`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `version` (
  `id` int NOT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `comment` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `timeInfo`
--

/*!50001 DROP VIEW IF EXISTS `timeInfo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = latin1 */;
/*!50001 SET character_set_results     = latin1 */;
/*!50001 SET collation_connection      = latin1_swedish_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`lopos_test`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `timeInfo` AS select max(`position`.`updated`) AS `lastInsert`,min(`position`.`updated`) AS `firstInsert` from `position` limit 1 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-06-14 13:57:57
