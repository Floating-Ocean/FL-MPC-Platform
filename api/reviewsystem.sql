/*
 Navicat Premium Dump SQL

 Source Server         : MySQL80
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : localhost:3306
 Source Schema         : reviewsystem

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 05/11/2024 15:24:54
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for books
-- ----------------------------
DROP TABLE IF EXISTS `books`;
CREATE TABLE `books`  (
  `BookID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Author` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Genre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `PublicationYear` int NULL DEFAULT NULL,
  `ISBN` varchar(13) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`BookID`) USING BTREE,
  UNIQUE INDEX `ISBN`(`ISBN` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

INSERT INTO `books` (`Title`, `Author`, `Genre`, `PublicationYear`, `ISBN`) 
VALUES ('1984', '乔治·奥威尔', '反乌托邦', 1949, '78-0451524935');

INSERT INTO `books` (`Title`, `Author`, `Genre`, `PublicationYear`, `ISBN`) 
VALUES ('百年孤独2', '加西亚·马尔克斯', '魔幻现实主义', 1967, '78-0060883287');

-- ----------------------------
-- Table structure for movies
-- ----------------------------
DROP TABLE IF EXISTS `movies`;
CREATE TABLE `movies`  (
  `MovieID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Director` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Genre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ReleaseYear` int NULL DEFAULT NULL,
  `Duration` int NULL DEFAULT NULL,
  PRIMARY KEY (`MovieID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

INSERT INTO `movies` (`Title`, `Director`, `Genre`, `ReleaseYear`,`Duration`) 
VALUES ('你的名字', '新海诚', '动画', 2016, '107');
INSERT INTO `movies` (`Title`, `Director`, `Genre`, `ReleaseYear`,`Duration`) 
VALUES ('亲爱的热爱的', '滨路晶', '动画', 2021, '169');

-- ----------------------------
-- Table structure for music
-- ----------------------------
DROP TABLE IF EXISTS `music`;
CREATE TABLE `music`  (
  `MusicID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Artist` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Album` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ReleaseYear` int NULL DEFAULT NULL,
  `Genre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`MusicID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

INSERT INTO `music` (`Title`, `Artist`, `Album`, `ReleaseYear`,`Genre`) 
VALUES ('Faded', 'Alan Walker', 'Different World', 2015, 'Electronic');

INSERT INTO `music` (`Title`, `Artist`, `Album`, `ReleaseYear`,`Genre`) 
VALUES ('罗生门(Follow)', '张子豪/梨冻紧', '罗生门(Follow)', 2020, 'Emotion');

-- ----------------------------
-- Table structure for reviews
-- ----------------------------
DROP TABLE IF EXISTS `reviews`;
CREATE TABLE `reviews`  (
  `ReviewID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `ContentType` enum('Book','Movie','Music') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `ContentID` int NOT NULL,
  `Rating` int NOT NULL,
  `Comment` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `CreatedAt` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ReviewID`) USING BTREE,
  INDEX `UserID`(`UserID` ASC) USING BTREE,
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `reviews_chk_1` CHECK ((`Rating` >= 1) and (`Rating` <= 5))
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `UserName` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Passwordhash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Email` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `is_admin` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`UserID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

INSERT INTO `users` (`UserID`,`UserName`, `Passwordhash`, `Email`,`is_admin`)
VALUES (1,'admin','scrypt:32768:8:1$TVQjN0ZOhllNBpV6$7126efc5020c943f595d587863f9462ff67a97f80b4a51a5ca684f1f61b51dc812ba9999aa25f2933611439615c5950fcf7de4e12912ba54bf95f44cfe71fd18','admin@example.com',TRUE);

-- ----------------------------
-- Triggers structure for table reviews
-- ----------------------------
DROP TRIGGER IF EXISTS `before_insert_reviews`;
delimiter ;;
CREATE TRIGGER `before_insert_reviews` BEFORE INSERT ON `reviews` FOR EACH ROW BEGIN
    IF NEW.ContentType = 'Book' THEN
        IF NOT EXISTS (SELECT 1 FROM books WHERE BookID = NEW.ContentID) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid BookID';
        END IF;
    ELSEIF NEW.ContentType = 'Movie' THEN
        IF NOT EXISTS (SELECT 1 FROM movies WHERE MovieID = NEW.ContentID) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid MovieID';
        END IF;
    ELSEIF NEW.ContentType = 'Music' THEN
        IF NOT EXISTS (SELECT 1 FROM music WHERE MusicID = NEW.ContentID) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid MusicID';
        END IF;
    END IF;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
