-- Drop existing table if it exists
DROP TABLE IF EXISTS requirements CASCADE;

-- Create requirements table
CREATE TABLE requirements (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    requirement_name VARCHAR(255) NOT NULL,
    description TEXT,
    requirement_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 