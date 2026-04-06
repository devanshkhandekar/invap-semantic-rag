CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_projects (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, project_id)
);

ALTER TABLE documents
ADD COLUMN IF NOT EXISTS project_id BIGINT REFERENCES projects(id);

CREATE INDEX IF NOT EXISTS idx_documents_project_id
ON documents(project_id);

CREATE INDEX IF NOT EXISTS idx_user_projects_user_id
ON user_projects(user_id);

CREATE INDEX IF NOT EXISTS idx_user_projects_project_id
ON user_projects(project_id);