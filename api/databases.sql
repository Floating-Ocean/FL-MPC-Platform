-- 创建用户表
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL
);

-- 创建模型表
CREATE TABLE model (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    user_id INT NOT NULL,
    file_directory VARCHAR(255) NOT NULL,
    is_user_uploaded BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES User (id)
);

-- 创建训练记录表
CREATE TABLE training_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    loss_list JSON NOT NULL,
    acc_list JSON NOT NULL,
    train_acc FLOAT NOT NULL,
    test_acc FLOAT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES Model (id)
);