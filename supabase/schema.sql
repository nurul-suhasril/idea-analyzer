-- Idea Analyzer Database Schema

-- Extractions table - stores all extracted content
CREATE TABLE IF NOT EXISTS extractions (
    id VARCHAR(12) PRIMARY KEY,
    url TEXT,
    source_type VARCHAR(20) NOT NULL, -- youtube, article, reddit, github, file
    title TEXT,
    raw_transcript TEXT,
    cleaned_transcript TEXT,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    slack_channel_id VARCHAR(50),
    slack_thread_ts VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis table - stores Claude's analysis results
CREATE TABLE IF NOT EXISTS analyses (
    id VARCHAR(12) PRIMARY KEY,
    extraction_id VARCHAR(12) REFERENCES extractions(id),
    executive_summary TEXT,
    full_report TEXT,
    preliminary_design TEXT,
    viability_score INTEGER,
    recommendation VARCHAR(20), -- pursue, research_more, pass
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_extractions_status ON extractions(status);
CREATE INDEX IF NOT EXISTS idx_extractions_source_type ON extractions(source_type);
CREATE INDEX IF NOT EXISTS idx_extractions_created_at ON extractions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_extraction_id ON analyses(extraction_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_extractions_updated_at ON extractions;
CREATE TRIGGER update_extractions_updated_at
    BEFORE UPDATE ON extractions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
