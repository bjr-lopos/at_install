-- MySQL dump 10.13  Distrib 5.7.30, for Linux (x86_64)
--
-- Host: localhost    Database: lopos_test
-- ------------------------------------------------------
-- Server version	5.7.30-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
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
  `id` int(4) NOT NULL AUTO_INCREMENT,
  `addr` int(5) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `addrid_UNIQUE` (`addr`),
  KEY `fk_anchor_1_idx` (`addr`),
  CONSTRAINT `fk_anchor_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cell`
--

DROP TABLE IF EXISTS `cell`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cell` (
  `core` int(4) NOT NULL,
  `edge` int(4) NOT NULL,
  PRIMARY KEY (`core`,`edge`),
  KEY `index1` (`core`),
  KEY `fk_cell_2_idx` (`edge`),
  CONSTRAINT `fk_cell_1` FOREIGN KEY (`core`) REFERENCES `anchor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_cell_2` FOREIGN KEY (`edge`) REFERENCES `anchor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cir`
--

DROP TABLE IF EXISTS `cir`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cir` (
  `reporter` int(5) NOT NULL,
  `dev` int(5) NOT NULL,
  `asn` int(20) NOT NULL DEFAULT '0',
  `rxQual` float(6,3) DEFAULT NULL,
  `fpPow` float(6,3) DEFAULT NULL,
  `rxPow` float(6,3) DEFAULT NULL,
  `cir0` int(6) DEFAULT NULL,
  `cir1` int(6) DEFAULT NULL,
  `cir2` int(6) DEFAULT NULL,
  `cir3` int(6) DEFAULT NULL,
  `cir4` int(6) DEFAULT NULL,
  `cir5` int(6) DEFAULT NULL,
  `cir6` int(6) DEFAULT NULL,
  `cir7` int(6) DEFAULT NULL,
  `cir8` int(6) DEFAULT NULL,
  `cir9` int(6) DEFAULT NULL,
  `cir10` int(6) DEFAULT NULL,
  `cir11` int(6) DEFAULT NULL,
  `cir12` int(6) DEFAULT NULL,
  `cir13` int(6) DEFAULT NULL,
  `cir14` int(6) DEFAULT NULL,
  `cir15` int(6) DEFAULT NULL,
  `cir16` int(6) DEFAULT NULL,
  `cir17` int(6) DEFAULT NULL,
  `cir18` int(6) DEFAULT NULL,
  `cir19` int(6) DEFAULT NULL,
  `cir20` int(6) DEFAULT NULL,
  `cir21` int(6) DEFAULT NULL,
  `cir22` int(6) DEFAULT NULL,
  `cir23` int(6) DEFAULT NULL,
  `cir24` int(6) DEFAULT NULL,
  `cir25` int(6) DEFAULT NULL,
  `cir26` int(6) DEFAULT NULL,
  `cir27` int(6) DEFAULT NULL,
  `cir28` int(6) DEFAULT NULL,
  `cir29` int(6) DEFAULT NULL,
  `cir30` int(6) DEFAULT NULL,
  `cir31` int(6) DEFAULT NULL,
  `cir32` int(6) DEFAULT NULL,
  `cir33` int(6) DEFAULT NULL,
  `cir34` int(6) DEFAULT NULL,
  `cir35` int(6) DEFAULT NULL,
  `cir36` int(6) DEFAULT NULL,
  `cir37` int(6) DEFAULT NULL,
  `cir38` int(6) DEFAULT NULL,
  `cir39` int(6) DEFAULT NULL,
  `cir40` int(6) DEFAULT NULL,
  `cir41` int(6) DEFAULT NULL,
  `cir42` int(6) DEFAULT NULL,
  `cir43` int(6) DEFAULT NULL,
  `cir44` int(6) DEFAULT NULL,
  `cir45` int(6) DEFAULT NULL,
  `cir46` int(6) DEFAULT NULL,
  `cir47` int(6) DEFAULT NULL,
  `cir48` int(6) DEFAULT NULL,
  `cir49` int(6) DEFAULT NULL,
  `cir50` int(6) DEFAULT NULL,
  `cir51` int(6) DEFAULT NULL,
  `cir52` int(6) DEFAULT NULL,
  `cir53` int(6) DEFAULT NULL,
  `cir54` int(6) DEFAULT NULL,
  `cir55` int(6) DEFAULT NULL,
  `cir56` int(6) DEFAULT NULL,
  `cir57` int(6) DEFAULT NULL,
  `cir58` int(6) DEFAULT NULL,
  `cir59` int(6) DEFAULT NULL,
  `cir60` int(6) DEFAULT NULL,
  `cir61` int(6) DEFAULT NULL,
  `cir62` int(6) DEFAULT NULL,
  `cir63` int(6) DEFAULT NULL,
  `cir64` int(6) DEFAULT NULL,
  `cir65` int(6) DEFAULT NULL,
  `cir66` int(6) DEFAULT NULL,
  `cir67` int(6) DEFAULT NULL,
  `cir68` int(6) DEFAULT NULL,
  `cir69` int(6) DEFAULT NULL,
  `cir70` int(6) DEFAULT NULL,
  `cir71` int(6) DEFAULT NULL,
  `cir72` int(6) DEFAULT NULL,
  `cir73` int(6) DEFAULT NULL,
  `cir74` int(6) DEFAULT NULL,
  `cir75` int(6) DEFAULT NULL,
  `cir76` int(6) DEFAULT NULL,
  `cir77` int(6) DEFAULT NULL,
  `cir78` int(6) DEFAULT NULL,
  `cir79` int(6) DEFAULT NULL,
  `cir80` int(6) DEFAULT NULL,
  `cir81` int(6) DEFAULT NULL,
  `cir82` int(6) DEFAULT NULL,
  `cir83` int(6) DEFAULT NULL,
  `cir84` int(6) DEFAULT NULL,
  `cir85` int(6) DEFAULT NULL,
  `cir86` int(6) DEFAULT NULL,
  `cir87` int(6) DEFAULT NULL,
  `cir88` int(6) DEFAULT NULL,
  `cir89` int(6) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`reporter`,`asn`),
  KEY `fk_cir_2_idx` (`updated`),
  KEY `fk_cir_2` (`dev`),
  CONSTRAINT `fk_cir_1` FOREIGN KEY (`reporter`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_cir_2` FOREIGN KEY (`dev`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device` (
  `addr` int(5) NOT NULL AUTO_INCREMENT,
  `mac` varchar(18) NOT NULL,
  `vbattATdfu` float(4,3) DEFAULT NULL,
  `added` timestamp(3) NULL DEFAULT CURRENT_TIMESTAMP(3),
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
  `addr` int(5) NOT NULL,
  `dfuStat` int(2) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `version` int(11) DEFAULT NULL,
  PRIMARY KEY (`addr`,`updated`),
  KEY `index2` (`addr`,`updated`),
  KEY `fk_dfu_2_idx` (`version`),
  CONSTRAINT `fk_dfu_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_dfu_2` FOREIGN KEY (`version`) REFERENCES `version` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `map`
--

DROP TABLE IF EXISTS `map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x1` int(11) DEFAULT NULL,
  `y1` int(11) DEFAULT NULL,
  `x2` int(11) DEFAULT NULL,
  `y2` int(11) DEFAULT NULL,
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
  `addr` int(5) NOT NULL,
  `x` int(11) DEFAULT NULL,
  `y` int(11) DEFAULT NULL,
  `z` int(11) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`addr`,`updated`),
  CONSTRAINT `fk_motion_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `position`
--

DROP TABLE IF EXISTS `position`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `position` (
  `addr` int(5) NOT NULL,
  `asn` int(20) NOT NULL DEFAULT '0',
  `x` int(7) DEFAULT NULL,
  `y` int(7) DEFAULT NULL,
  `z` int(7) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `numHyperbola` int(3) DEFAULT NULL,
  `numPyTime` int(5) DEFAULT NULL,
  PRIMARY KEY (`addr`,`updated`),
  CONSTRAINT `fk_position_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stat`
--

DROP TABLE IF EXISTS `stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stat` (
  `addr` int(5) NOT NULL,
  `asn` int(16) NOT NULL DEFAULT '0',
  `version` int(11) NOT NULL DEFAULT '0',
  `mac` varchar(17) DEFAULT NULL,
  `vbattRatio` int(3) NOT NULL DEFAULT '0',
  `drift` int(6) NOT NULL DEFAULT '0',
  `beaconRSSI` int(3) NOT NULL DEFAULT '0',
  `devRSSI` int(3) NOT NULL DEFAULT '0',
  `beaconRatio` int(3) NOT NULL DEFAULT '0',
  `sgTxRatio` int(3) NOT NULL DEFAULT '0',
  `sgRxRatio` int(3) NOT NULL DEFAULT '0',
  `uwbTxRatio` int(3) NOT NULL DEFAULT '0',
  `uwbRxRatio` int(3) NOT NULL DEFAULT '0',
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`addr`,`updated`),
  KEY `index2` (`addr`,`asn`),
  CONSTRAINT `fk_stat_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
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
  `SFmax` int(5) NOT NULL,
  `SFticks` int(5) NOT NULL,
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
  `id` int(4) NOT NULL AUTO_INCREMENT,
  `addr` int(5) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `addr_UNIQUE` (`addr`),
  KEY `fk_tag_1_idx` (`addr`),
  CONSTRAINT `fk_tag_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tdoa`
--

DROP TABLE IF EXISTS `tdoa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tdoa` (
  `edge` int(4) NOT NULL,
  `sync` int(4) NOT NULL,
  `tag` int(4) NOT NULL,
  `asn` int(20) NOT NULL DEFAULT '0',
  `ts` int(13) DEFAULT '0',
  `drift` int(10) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`edge`,`sync`,`tag`,`asn`),
  KEY `fk_tdoa_2_idx` (`sync`),
  KEY `fk_tdoa_3_idx` (`tag`),
  CONSTRAINT `fk_tdoa_1` FOREIGN KEY (`edge`) REFERENCES `anchor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_tdoa_2` FOREIGN KEY (`sync`) REFERENCES `anchor` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_tdoa_3` FOREIGN KEY (`tag`) REFERENCES `tag` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
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
  `addr` int(5) NOT NULL DEFAULT '0',
  `scheduleAT` int(4) NOT NULL,
  `scenario` int(3) NOT NULL DEFAULT '0',
  `actor` int(2) NOT NULL,
  `persistent` int(1) NOT NULL DEFAULT '0',
  `active` int(1) NOT NULL DEFAULT '0',
  `repeatSlots` int(4) NOT NULL DEFAULT '0',
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`addr`,`scheduleAT`,`scenario`,`actor`,`updated`),
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
  `devA` int(5) NOT NULL,
  `devB` int(5) NOT NULL,
  `asn` int(20) NOT NULL DEFAULT '0',
  `dist` int(11) DEFAULT '0',
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`devA`,`devB`),
  KEY `fk_twr_2_idx` (`devB`),
  CONSTRAINT `fk_twr_1` FOREIGN KEY (`devA`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_twr_2` FOREIGN KEY (`devB`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uwbstat`
--

DROP TABLE IF EXISTS `uwbstat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uwbstat` (
  `devTx` int(5) NOT NULL,
  `devRx` int(5) NOT NULL,
  `asn` int(20) NOT NULL DEFAULT '0',
  `rxQual` float(6,3) DEFAULT NULL,
  `fpPow` float(6,3) DEFAULT NULL,
  `rxPow` float(6,3) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (`devTx`,`devRx`),
  KEY `fk_uwbstat_2_idx` (`devRx`),
  CONSTRAINT `fk_uwbstat_1` FOREIGN KEY (`devTx`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_uwbstat_2` FOREIGN KEY (`devRx`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `version` (
  `id` int(11) NOT NULL,
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

-- Dump completed on 2020-05-28 11:15:55
