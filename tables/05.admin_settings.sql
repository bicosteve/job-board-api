CREATE TABLE IF NOT EXISTS admin_setting(
    setting_id INT PRIMARY KEY AUTO_INCREMENT,
    is_deactivated INT NOT NULL DEFAULT 0,
    admin_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id)  ON DELETE CASCADE
);

CREATE INDEX admin_setting_idx ON admin_setting(setting_id);