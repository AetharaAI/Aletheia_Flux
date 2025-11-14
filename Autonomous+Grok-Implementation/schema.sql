-- Agent Discovery System - Database Schema
-- Extends Aletheia Flux database with agent discovery tables

-- ============================================================================
-- DISCOVERED AGENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS discovered_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    
    -- Classification
    framework VARCHAR(100),                    -- 'LangChain', 'CrewAI', 'Custom', etc.
    category VARCHAR(100),                     -- 'research', 'coding', 'automation', etc.
    tags TEXT[] DEFAULT '{}',
    capabilities JSONB DEFAULT '[]',
    
    -- Technical Details
    endpoint_url VARCHAR(500),
    source_url VARCHAR(500) NOT NULL,
    documentation_url VARCHAR(500),
    
    -- Contact Information
    contact_email VARCHAR(255),
    github_url VARCHAR(500),
    twitter_handle VARCHAR(100),
    linkedin_url VARCHAR(500),
    
    -- Discovery Metadata
    discovered_at TIMESTAMP DEFAULT NOW(),
    discovered_by VARCHAR(50) DEFAULT 'discovery_system',
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Verification Status
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verified_by VARCHAR(100),
    verification_notes TEXT,
    
    -- Registration Status
    registered BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMP,
    aetherpro_agent_id UUID,                   -- Links to main agents table once registered
    
    -- Source Data (for reference)
    raw_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- OUTREACH TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES discovered_agents(id) ON DELETE CASCADE,
    
    -- Contact Details
    contact_method VARCHAR(50) NOT NULL,       -- 'email', 'twitter', 'github', 'linkedin'
    contact_address VARCHAR(255) NOT NULL,
    
    -- Outreach Content
    message_template TEXT NOT NULL,
    personalization_data JSONB,
    subject_line VARCHAR(200),
    
    -- Status Tracking
    outreach_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'sent', 'bounced', 'replied', 'registered', 'declined'
    
    -- Timing
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    replied_at TIMESTAMP,
    registered_at TIMESTAMP,
    
    -- Response Data
    reply_content TEXT,
    reply_sentiment VARCHAR(50),               -- 'positive', 'neutral', 'negative'
    
    -- Follow-up
    follow_up_count INTEGER DEFAULT 0,
    last_follow_up TIMESTAMP,
    next_follow_up TIMESTAMP,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- DISCOVERY RUNS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS discovery_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Run Configuration
    run_type VARCHAR(50) NOT NULL,             -- 'scheduled', 'manual', 'targeted', 'test'
    target_sources TEXT[],
    keywords TEXT[],
    max_results INTEGER DEFAULT 50,
    
    -- Results Summary
    agents_found INTEGER DEFAULT 0,
    agents_classified INTEGER DEFAULT 0,
    agents_stored INTEGER DEFAULT 0,
    agents_duplicates INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'running',      -- 'running', 'completed', 'failed', 'cancelled'
    error_message TEXT,
    
    -- Performance Metrics
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- API Usage Stats
    grok_calls INTEGER DEFAULT 0,
    tavily_calls INTEGER DEFAULT 0,
    firecrawl_calls INTEGER DEFAULT 0,
    minimax_tokens INTEGER DEFAULT 0,
    
    -- Cost Tracking (in USD)
    estimated_cost DECIMAL(10,4),
    
    -- Metadata
    thinking_trace JSONB,
    config JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- AGENT VERIFICATION QUEUE
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_verification_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES discovered_agents(id) ON DELETE CASCADE,
    
    -- Priority
    priority INTEGER DEFAULT 0,                -- Higher = more important
    confidence_score DECIMAL(3,2),
    
    -- Assignment
    assigned_to VARCHAR(100),
    assigned_at TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',      -- 'pending', 'in_progress', 'completed', 'rejected'
    
    -- Verification Data
    verification_checklist JSONB,             -- Manual verification steps
    verification_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- ============================================================================
-- AGENT CATEGORIES (Reference Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    parent_category_id UUID REFERENCES agent_categories(id),
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default categories
INSERT INTO agent_categories (name, slug, description, display_order) VALUES
    ('Research', 'research', 'Agents that perform research, web search, and information gathering', 1),
    ('Development', 'development', 'Agents that write code, debug, and assist with software development', 2),
    ('Productivity', 'productivity', 'Agents that enhance productivity, automate tasks, and manage workflows', 3),
    ('Creative', 'creative', 'Agents that generate content, art, music, or other creative outputs', 4),
    ('Data Analysis', 'data-analysis', 'Agents that analyze data, generate insights, and create visualizations', 5),
    ('Automation', 'automation', 'Agents that automate repetitive tasks and business processes', 6),
    ('Customer Support', 'customer-support', 'Agents that handle customer inquiries and support tickets', 7),
    ('Education', 'education', 'Agents that teach, tutor, and facilitate learning', 8)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Discovered Agents
CREATE INDEX IF NOT EXISTS idx_discovered_agents_category ON discovered_agents(category);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_framework ON discovered_agents(framework);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_verified ON discovered_agents(verified);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_registered ON discovered_agents(registered);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_confidence ON discovered_agents(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_discovered_at ON discovered_agents(discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_discovered_agents_tags ON discovered_agents USING GIN(tags);

-- Outreach
CREATE INDEX IF NOT EXISTS idx_agent_outreach_status ON agent_outreach(outreach_status);
CREATE INDEX IF NOT EXISTS idx_agent_outreach_agent_id ON agent_outreach(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_outreach_sent_at ON agent_outreach(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_outreach_next_follow_up ON agent_outreach(next_follow_up);

-- Discovery Runs
CREATE INDEX IF NOT EXISTS idx_discovery_runs_status ON discovery_runs(status);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_started_at ON discovery_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_run_type ON discovery_runs(run_type);

-- Verification Queue
CREATE INDEX IF NOT EXISTS idx_verification_queue_status ON agent_verification_queue(status);
CREATE INDEX IF NOT EXISTS idx_verification_queue_priority ON agent_verification_queue(priority DESC);
CREATE INDEX IF NOT EXISTS idx_verification_queue_assigned_to ON agent_verification_queue(assigned_to);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_discovered_agents_updated_at BEFORE UPDATE ON discovered_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_outreach_updated_at BEFORE UPDATE ON agent_outreach
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Unverified high-confidence agents
CREATE OR REPLACE VIEW unverified_high_confidence_agents AS
SELECT 
    id,
    name,
    slug,
    description,
    category,
    framework,
    confidence_score,
    contact_email,
    github_url,
    discovered_at
FROM discovered_agents
WHERE verified = FALSE
    AND confidence_score >= 0.7
ORDER BY confidence_score DESC, discovered_at DESC;

-- Agents ready for outreach
CREATE OR REPLACE VIEW agents_ready_for_outreach AS
SELECT 
    da.id,
    da.name,
    da.slug,
    da.contact_email,
    da.github_url,
    da.twitter_handle,
    da.category,
    da.framework,
    da.verified
FROM discovered_agents da
LEFT JOIN agent_outreach ao ON da.id = ao.agent_id
WHERE da.verified = TRUE
    AND da.registered = FALSE
    AND (da.contact_email IS NOT NULL OR da.github_url IS NOT NULL)
    AND (ao.id IS NULL OR ao.outreach_status = 'pending')
ORDER BY da.confidence_score DESC;

-- Discovery run statistics
CREATE OR REPLACE VIEW discovery_run_stats AS
SELECT 
    DATE(started_at) as run_date,
    COUNT(*) as total_runs,
    SUM(agents_found) as total_agents_found,
    SUM(agents_stored) as total_agents_stored,
    AVG(duration_seconds) as avg_duration_seconds,
    SUM(estimated_cost) as total_cost
FROM discovery_runs
WHERE status = 'completed'
GROUP BY DATE(started_at)
ORDER BY run_date DESC;

-- Outreach performance metrics
CREATE OR REPLACE VIEW outreach_performance AS
SELECT 
    contact_method,
    COUNT(*) as total_sent,
    COUNT(CASE WHEN opened_at IS NOT NULL THEN 1 END) as opened,
    COUNT(CASE WHEN replied_at IS NOT NULL THEN 1 END) as replied,
    COUNT(CASE WHEN registered_at IS NOT NULL THEN 1 END) as registered,
    ROUND(100.0 * COUNT(CASE WHEN replied_at IS NOT NULL THEN 1 END) / NULLIF(COUNT(*), 0), 2) as reply_rate,
    ROUND(100.0 * COUNT(CASE WHEN registered_at IS NOT NULL THEN 1 END) / NULLIF(COUNT(*), 0), 2) as conversion_rate
FROM agent_outreach
WHERE sent_at IS NOT NULL
GROUP BY contact_method;

-- ============================================================================
-- ROW LEVEL SECURITY (Optional - if using Supabase Auth)
-- ============================================================================

-- Enable RLS on tables
-- ALTER TABLE discovered_agents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE agent_outreach ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE discovery_runs ENABLE ROW LEVEL SECURITY;

-- Policies (example - adjust based on your auth setup)
-- CREATE POLICY "Public read access for verified agents" ON discovered_agents
--     FOR SELECT USING (verified = TRUE);

-- CREATE POLICY "Admin full access" ON discovered_agents
--     FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get agents discovered today
-- SELECT * FROM discovered_agents 
-- WHERE DATE(discovered_at) = CURRENT_DATE;

-- Get top frameworks
-- SELECT framework, COUNT(*) as count 
-- FROM discovered_agents 
-- WHERE verified = TRUE 
-- GROUP BY framework 
-- ORDER BY count DESC;

-- Get outreach success rate
-- SELECT * FROM outreach_performance;

-- Get agents needing follow-up
-- SELECT * FROM agent_outreach 
-- WHERE outreach_status = 'sent' 
--     AND next_follow_up <= NOW() 
-- ORDER BY next_follow_up;
