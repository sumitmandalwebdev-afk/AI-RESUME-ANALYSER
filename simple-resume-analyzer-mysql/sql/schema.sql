-- ============================================================
-- ResumeIQ — MySQL Schema
-- MySQL Workbench / phpMyAdmin / terminal me run karo
-- ============================================================

CREATE DATABASE IF NOT EXISTS resume_iq
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE resume_iq;

-- Users table (login / signup)
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name     VARCHAR(150) DEFAULT '',
  is_admin      TINYINT(1) NOT NULL DEFAULT 0,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Resume analyses
CREATE TABLE IF NOT EXISTS resume_analyses (
  id               CHAR(36) PRIMARY KEY,          -- UUID
  user_id          INT NOT NULL,
  file_name        VARCHAR(255) NOT NULL,
  file_path        VARCHAR(500) NOT NULL,         -- local path under uploads/
  extracted_text   MEDIUMTEXT,
  job_description  TEXT,
  ats_score        INT,
  job_match_score  INT,
  feedback         JSON,                          -- full AI result
  status           ENUM('pending','processing','completed','failed')
                   NOT NULL DEFAULT 'pending',
  error_message    TEXT,
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                   ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- Helpful indexes
CREATE INDEX idx_analyses_user ON resume_analyses(user_id);
CREATE INDEX idx_analyses_created ON resume_analyses(created_at);

-- ============================================================
-- Optional: pehla admin user (password = admin123)
-- Password hash werkzeug generate karega, isliye app se signup
-- karke baad me is_admin = 1 set karna better hai.
-- ============================================================
-- UPDATE users SET is_admin = 1 WHERE email = 'you@example.com';
