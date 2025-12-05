CREATE TABLE `job_applications` (
    `application_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `job_id` INT NOT NULL,
    `status` TINYINT NOT NULL DEFAULT 1,
    `cover_letter` TEXT,
    `resume_url` VARCHAR(255),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `modified_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_app_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`user_id`),
    CONSTRAINT `fk_app_job` FOREIGN KEY (`job_id`) REFERENCES `jobs`(`job_id`),
    CONSTRAINT `uq_user_job` UNIQUE (`user_id`, `job_id`)
) ENGINE=InnoDB;

CREATE INDEX `idx_job_app_user` ON `job_applications`(`user_id`);

CREATE INDEX `idx_job_app_job` ON `job_applications`(`job_id`);

CREATE INDEX `idx_job_app_user_status` ON `job_applications`(`user_id`,`status`);

CREATE INDEX `idx_job_app_job_status` ON `job_applications`(`job_id`,`status`);
