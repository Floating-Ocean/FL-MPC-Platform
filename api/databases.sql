-- 创建用户表
CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL
);

-- 创建模型表
CREATE TABLE Model (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    user_id INT NOT NULL,
    file_directory VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User (id)
);

-- 创建训练记录表
CREATE TABLE TrainingRecord (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    loss_list TEXT,
    acc_list TEXT,
    FOREIGN KEY (model_id) REFERENCES Model (id)
);