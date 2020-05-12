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
  `asn` int(20) NOT NULL DEFAULT '0',
  `vbatt` float(4,3) DEFAULT NULL,
  `hit_beacon` int(10) DEFAULT NULL,
  `hit_sgTX` int(10) DEFAULT NULL,
  `hit_sgRX` int(10) DEFAULT NULL,
  `hit_uwbTX` int(10) DEFAULT NULL,
  `hit_uwbRX` int(10) DEFAULT NULL,
  `drift` int(6) DEFAULT NULL,
  `beaconRSSI` int(3) DEFAULT NULL,
  `devRSSI` int(3) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `updated` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  `cnt_beacon` int(10) DEFAULT NULL,
  `cnt_sgTX` int(10) DEFAULT NULL,
  `cnt_sgRX` int(10) DEFAULT NULL,
  `cnt_uwbTX` int(10) DEFAULT NULL,
  `cnt_uwbRX` int(10) DEFAULT NULL,
  PRIMARY KEY (`addr`,`updated`),
  KEY `fk_stat_2_idx` (`version`),
  CONSTRAINT `fk_stat_1` FOREIGN KEY (`addr`) REFERENCES `device` (`addr`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_stat_2` FOREIGN KEY (`version`) REFERENCES `version` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
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


/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-05-10 19:21:50
