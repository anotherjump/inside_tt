CREATE DATABASE `msgsrv`;
use `msgsrv`;
CREATE TABLE `users` (
  `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `users_UN` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE `messages` (
  `msgid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `message` text NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`msgid`),
  KEY `messages_FK` (`name`),
  CONSTRAINT `messages_FK` FOREIGN KEY (`name`) REFERENCES `users` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO users (name, password) VALUES
("testuser1", "passwd1"),
("testuser2", "passwd2"),
("testuser3", "passwd3");