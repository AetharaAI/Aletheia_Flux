-- ============================================================================
-- Agent Discovery System Database Schema
-- ============================================================================
-- This schema extends the Aletheia Flux database with tables for
-- autonomous AI agent discovery and outreach management.
-- ============================================================================

-- Discovered agents (before manual verification)
CREATE TABLE IF NOT EXISTS discovered_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,

    -- Classification
    framework VARCHAR(100),
    category VARCHAR(100),
    tags TEXT[],
    capabilities JSONB,

    -- Technical
    endpoint_url VARCHAR(500),
    source_url VARCHAR(500) NOT NULL,
    documentation_url VARCHAR(500),

    -- Contacts
    contact_email VARCHAR(255),
    github_url VARCHAR(500),
    twitter_handle VARCHAR(100),

    -- Discovery Metadata
    discovered_at TIMESTAMP DEFAULT NOW(),
    discovered_by VARCHAR(50) DEFAULT 'grok_sweep',
    confidence_score DECIMAL(3,2),

    -- Verification Status
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verified_by VARCHAR(255),
    verification_notes TEXT,

    -- Registration Status
    registered BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMP,
    aetherpro_agent_id UUID,

    -- Source Data
    raw_data JSONB,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Outreach tracking
CREATE TABLE IF NOT EXISTS agent_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES discovered_agents(id) ON DELETE CASCADE,

    -- Contact Details
    contact_method VARCHAR(50), -- 'email', 'twitter', 'github'
    contact_address VARCHAR(255),

    -- Outreach
    outreach_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'replied', 'registered'
    message_template TEXT,
    personalization_data JSONB,

    -- Tracking
    sent_at TIMESTAMP,
    replied_at TIMESTAMP,
    registered_at TIMESTAMP,

    -- Notes
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Discovery runs (batches)
CREATE TABLE IF NOT EXISTS discovery_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Run Info
    run_type VARCHAR(50), -- 'scheduled', 'manual', 'targeted'
    target_sources TEXT[],
    keywords TEXT[],

    -- Results
    agents_found INTEGER DEFAULT 0,
    agents_classified INTEGER DEFAULT 0,
    agents_stored INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(50) DEFAULT 'running', -- 'running', 'completed', 'failed'
    error_message TEXT,

    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,

    -- Metadata
    thinking_trace JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent verification queue
CREATE TABLE IF NOT EXISTS agent_verification_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES discovered_agents(id) ON DELETE CASCADE,

    -- Queue Info
    priority_score DECIMAL(3,2), -- Confidence score
    assigned_to VARCHAR(255),
    assigned_at TIMESTAMP,

    -- Verification
    verification_status VARCHAR(50) DEFAULT 'pending',
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verifier_notes TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent categories reference
CREATE TABLE IF NOT EXISTS agent_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_category_id INTEGER REFERENCES agent_categories(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default categories
INSERT INTO agent_categories (name, description) VALUES
    ('research', 'AI agents for research and information gathering'),
    ('coding', 'AI agents for software development and programming'),
    ('automation', 'AI agents for workflow and task automation'),
    ('productivity', 'AI agents for personal and business productivity'),
    ('creative', 'AI agents for content creation and design'),
    ('customer service', 'AI agents for customer support and service'),
    ('data analysis', 'AI agents for data processing and analytics'),
    ('security', 'AI agents for cybersecurity and threat detection')
ON CONFLICT (name) DO NOTHING;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_discovered_agents_category ON discovered_agents(category);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_framework ON discovered_agents(framework);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_verified ON discovered_agents(verified);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_confidence ON discovered_agents(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_registered ON discovered_agents(registered);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_discovered_at ON discovered_agents(discovered_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_outreach_agent_id ON agent_outreach(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_outreach_status ON agent_outreach(outreach_status);
CREATE INDEX IF NOT EXISTS idx_agent_outreach_sent_at ON agent_outreach(sent_at DESC);

CREATE INDEX IF NOT EXISTS idx_discovery_runs_status ON discovery_runs(status);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_started_at ON discovery_runs(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_verification_queue_priority ON agent_verification_queue(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_verification_queue_status ON agent_verification_queue(verification_status);

-- Views for analytics

-- High-confidence agents needing verification
CREATE OR REPLACE VIEW unverified_high_confidence_agents AS
SELECT *
FROM discovered_agents
WHERE verified = FALSE
  AND confidence_score >= 0.7
ORDER BY confidence_score DESC;

-- Agents ready for outreach
CREATE OR REPLACE VIEW agents_ready_for_outreach AS
SELECT da.*
FROM discovered_agents da
LEFT JOIN agent_outreach ao ON da.id = ao.agent_id
WHERE da.verified = TRUE
  AND da.registered = FALSE
  AND (ao.id IS NULL OR ao.outreach_status = 'pending')
ORDER BY da.confidence_score DESC;

-- Discovery run statistics
CREATE OR REPLACE VIEW discovery_run_stats AS
SELECT
    DATE(started_at) as run_date,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
    SUM(agents_found) as total_agents_found,
    SUM(agents_classified) as total_agents_classified,
    SUM(agents_stored) as total_agents_stored,
    AVG(duration_seconds) as avg_duration_seconds
FROM discovery_runs
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(started_at)
ORDER BY run_date DESC;

-- Outreach performance metrics
CREATE OR REPLACE VIEW outreach_performance AS
SELECT
    outreach_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM agent_outreach
WHERE sent_at >= NOW() - INTERVAL '30 days'
GROUP BY outreach_status
ORDER BY count DESC;

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to discovered_agents
DROP TRIGGER IF EXISTS update_discovered_agents_updated_at ON discovered_agents;
CREATE TRIGGER update_discovered_agents_updated_at
    BEFORE UPDATE ON discovered_agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- RPC Functions for statistics

-- Get agents by category
CREATE OR REPLACE FUNCTION get_agents_by_category()
RETURNS TABLE(
    category_name VARCHAR(100),
    agent_count BIGINT,
    verified_count BIGINT,
    registered_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ac.name,
        COUNT(da.id) as agent_count,
        COUNT(CASE WHEN da.verified THEN 1 END) as verified_count,
        COUNT(CASE WHEN da.registered THEN 1 END) as registered_count
    FROM agent_categories ac
    LEFT JOIN discovered_agents da ON ac.name = da.category
    GROUP BY ac.name, ac.id
    ORDER BY agent_count DESC;
END;
$$ LANGUAGE plpgsql;

-- Get outreach statistics
CREATE OR REPLACE FUNCTION get_outreach_stats()
RETURNS TABLE(
    total_sent BIGINT,
    total_replied BIGINT,
    total_registered BIGINT,
    reply_rate DECIMAL,
    conversion_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(CASE WHEN ao.sent_at IS NOT NULL THEN 1 END) as total_sent,
        COUNT(CASE WHEN ao.replied_at IS NOT NULL THEN 1 END) as total_replied,
        COUNT(CASE WHEN ao.registered_at IS NOT NULL THEN 1 END) as total_registered,
        ROUND(
            CASE
                WHEN COUNT(CASE WHEN ao.sent_at IS NOT NULL THEN 1 END) = 0 THEN 0
                ELSE COUNT(CASE WHEN ao.replied_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(CASE WHEN ao.sent_at IS NOT NULL THEN 1 END)
            END, 2
        ) as reply_rate,
        ROUND(
            CASE
                WHEN COUNT(CASE WHEN ao.sent_at IS NOT NULL THEN 1 END) = 0 THEN 0
                ELSE COUNT(CASE WHEN ao.registered_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(CASE WHEN ao.sent_at IS NOT NULL THEN 1 END)
            END, 2
        ) as conversion_rate
    FROM agent_outreach ao;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- End of Schema
-- ============================================================================
