-- Initial database schema with pgvector support
-- Run this script to set up the database

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create approval_requests table
CREATE TABLE IF NOT EXISTS approval_requests (
    id SERIAL PRIMARY KEY,
    request_source VARCHAR(50) NOT NULL,
    requester_name VARCHAR(100) NOT NULL,
    approver_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    justification_text TEXT,
    metadata_json JSONB,
    search_vector vector(1024),  -- Cohere embed-english-v3.0 dimension
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_approval_requests_source ON approval_requests(request_source);
CREATE INDEX IF NOT EXISTS idx_approval_requests_approver ON approval_requests(approver_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_created ON approval_requests(created_at DESC);

-- Create vector index for semantic search (using HNSW for better performance)
CREATE INDEX IF NOT EXISTS idx_approval_requests_vector ON approval_requests 
USING hnsw (search_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_approval_requests_updated_at
    BEFORE UPDATE ON approval_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();



