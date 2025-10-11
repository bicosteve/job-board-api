CREATE TABLE profile(
    profile_id INT AUTO_INCREMENT PRIMARY KEY, 
    email VARCHAR(100) NOT NULL, 
    hash TEXT NOT NULL, 
    photo TEXT, 
    status SMALLINT NOT NULL DEFAULT 0, 
    reset_token TEXT, 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_profile_id ON profile(profile_id);



