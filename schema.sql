-- =====================================================================
-- IntelliHire AI Mock Interview Platform - Relational MySQL Schema
-- B.Tech Information Technology Individual Capstone Project
-- Compatible with MySQL 8.0+ / MariaDB 10.4+ / XAMPP
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `intellihire` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `intellihire`;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'student',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Resumes Table
CREATE TABLE IF NOT EXISTS `resumes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `filename` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(512) NOT NULL,
  `raw_text` MEDIUMTEXT NULL,
  `parsed_skills` JSON NULL,
  `recommended_domains` JSON NULL,
  `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX `idx_resume_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. User Verified Skills Table
CREATE TABLE IF NOT EXISTS `user_skills` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `skill_name` VARCHAR(100) NOT NULL,
  `proficiency` VARCHAR(30) DEFAULT 'Intermediate',
  `source` VARCHAR(20) DEFAULT 'extracted',
  `added_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_user_skill` (`user_id`, `skill_name`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Target Companies Table
CREATE TABLE IF NOT EXISTS `companies` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `description` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Question Bank Table
CREATE TABLE IF NOT EXISTS `questions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `company` VARCHAR(100) NOT NULL DEFAULT 'General',
  `skill` VARCHAR(100) NOT NULL,
  `interview_type` VARCHAR(30) NOT NULL DEFAULT 'Technical',
  `difficulty` VARCHAR(20) NOT NULL DEFAULT 'Medium',
  `category` VARCHAR(100) NULL,
  `question_text` TEXT NOT NULL,
  `model_answer` TEXT NOT NULL,
  `keywords` JSON NOT NULL,
  `follow_up_to_id` INT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`follow_up_to_id`) REFERENCES `questions` (`id`) ON DELETE SET NULL,
  INDEX `idx_question_filter` (`company`, `skill`, `difficulty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Interview Sessions Table
CREATE TABLE IF NOT EXISTS `interview_sessions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `session_uuid` VARCHAR(36) NOT NULL UNIQUE,
  `user_id` INT NOT NULL,
  `company` VARCHAR(100) NOT NULL,
  `skill` VARCHAR(100) NOT NULL,
  `interview_type` VARCHAR(30) NOT NULL DEFAULT 'Technical',
  `difficulty` VARCHAR(20) NOT NULL DEFAULT 'Medium',
  `question_count` INT NOT NULL DEFAULT 5,
  `current_index` INT NOT NULL DEFAULT 0,
  `status` VARCHAR(30) NOT NULL DEFAULT 'in_progress',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` DATETIME NULL,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX `idx_session_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Interview Question Log Table
CREATE TABLE IF NOT EXISTS `interview_questions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `session_id` INT NOT NULL,
  `question_id` INT NULL,
  `order_index` INT NOT NULL,
  `question_text` TEXT NOT NULL,
  `model_answer` TEXT NOT NULL,
  `keywords` JSON NULL,
  `difficulty` VARCHAR(20) NOT NULL DEFAULT 'Medium',
  `question_source` VARCHAR(50) NOT NULL,
  `user_answer` TEXT NULL,
  `similarity_score` FLOAT DEFAULT 0.0,
  `keyword_coverage` FLOAT DEFAULT 0.0,
  `final_score` FLOAT DEFAULT 0.0,
  `strengths` JSON NULL,
  `weaknesses` JSON NULL,
  `missing_concepts` JSON NULL,
  `feedback` TEXT NULL,
  `answered_at` DATETIME NULL,
  FOREIGN KEY (`session_id`) REFERENCES `interview_sessions` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE SET NULL,
  INDEX `idx_session_order` (`session_id`, `order_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Final Performance Reports Table
CREATE TABLE IF NOT EXISTS `performance_reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `session_id` INT NOT NULL UNIQUE,
  `user_id` INT NOT NULL,
  `overall_score` FLOAT NOT NULL DEFAULT 0.0,
  `average_score` FLOAT NOT NULL DEFAULT 0.0,
  `technical_knowledge_score` FLOAT NOT NULL DEFAULT 0.0,
  `readiness_percentage` FLOAT NOT NULL DEFAULT 0.0,
  `strong_topics` JSON NULL,
  `weak_topics` JSON NULL,
  `missing_concepts` JSON NULL,
  `recommendations` JSON NULL,
  `summary_notes` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`session_id`) REFERENCES `interview_sessions` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
