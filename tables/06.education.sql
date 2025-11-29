CREATE TABLE IF NOT EXISTS `education`(
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `level` ENUM('Secondary', 'University','Certificates') NOT NULL,
    `institution` VARCHAR(255) NOT NULL,
    `field` VARCHAR(150),
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `description` TEXT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`) ON DELETE CASCADE
);

CREATE INDEX `ed_idx` ON `education`(`id`);
