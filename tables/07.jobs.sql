CREATE TABLE IF NOT EXISTS `jobs` (
    `job_id` INT AUTO_INCREMENT PRIMARY KEY,
    `admin_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `requirements` TEXT,
    `location` VARCHAR(150),
    `employment_type` ENUM('1', '2', '3', '4') NOT NULL DEFAULT '1',
    `salary_range` VARCHAR(100),
    `company_name` VARCHAR(150) NOT NULL,
    `application_url` VARCHAR(255),
    `deadline` DATE,
    `status` ENUM('5', '6', '7') DEFAULT '5',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`admin_id`) REFERENCES `admins`(`admin_id`) ON DELETE CASCADE
);

CREATE INDEX `job_admin_idx` ON `jobs`(`admin_id`);
