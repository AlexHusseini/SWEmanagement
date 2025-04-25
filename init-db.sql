DROP TABLE IF EXISTS requirements CASCADE;
DROP TABLE IF EXISTS effort_tracking;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS risks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    owner TEXT,
    project_description TEXT,
    project_scope TEXT,
    target_users TEXT,
    technology_stack TEXT,
    platform TEXT
);

CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    role TEXT,
    responsibilities TEXT,
    skill_level TEXT
);

CREATE TABLE risks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
	risk_name TEXT NOT NULL,
    risk_description TEXT NOT NULL,
    risk_status TEXT
);

CREATE TABLE requirements (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    requirement_name TEXT NOT NULL,
    description TEXT,
    requirement_type TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE effort_tracking (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    requirement_id INTEGER REFERENCES requirements(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    requirements_analysis NUMERIC DEFAULT 0,
    designing NUMERIC DEFAULT 0,
    coding NUMERIC DEFAULT 0,
    testing NUMERIC DEFAULT 0,
    project_management NUMERIC DEFAULT 0
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create default admin user
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Project Manager'); 