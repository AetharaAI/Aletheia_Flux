-- Migration: create_aletheia_schema
-- Created at: 1762237867

-- Users table (extends Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  preferences JSONB DEFAULT '{}'::jsonb
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL DEFAULT 'New Conversation',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  thinking_trace JSONB,
  sources JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Sources table
CREATE TABLE IF NOT EXISTS sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL,
  url TEXT NOT NULL,
  title TEXT,
  content TEXT,
  credibility_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Search queries table
CREATE TABLE IF NOT EXISTS search_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID NOT NULL,
  query TEXT NOT NULL,
  results_count INTEGER,
  execution_time INTEGER,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- File uploads table
CREATE TABLE IF NOT EXISTS file_uploads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size BIGINT,
  processed_at TIMESTAMPTZ,
  insights JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_sources_message_id ON sources(message_id);
CREATE INDEX IF NOT EXISTS idx_search_queries_message_id ON search_queries(message_id);
CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads(user_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_uploads ENABLE ROW LEVEL SECURITY;

-- RLS Policies (allow both anon and service_role for edge function compatibility)
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can insert own profile" ON users
  FOR INSERT WITH CHECK (auth.uid() = id OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can view own conversations" ON conversations
  FOR SELECT USING (user_id = auth.uid() OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can create own conversations" ON conversations
  FOR INSERT WITH CHECK (user_id = auth.uid() OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can update own conversations" ON conversations
  FOR UPDATE USING (user_id = auth.uid() OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can delete own conversations" ON conversations
  FOR DELETE USING (user_id = auth.uid() OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can view messages in own conversations" ON messages
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM conversations WHERE conversations.id = messages.conversation_id AND conversations.user_id = auth.uid())
    OR auth.role() IN ('anon', 'service_role')
  );

CREATE POLICY "Users can create messages in own conversations" ON messages
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM conversations WHERE conversations.id = messages.conversation_id AND conversations.user_id = auth.uid())
    OR auth.role() IN ('anon', 'service_role')
  );

CREATE POLICY "Users can view sources" ON sources
  FOR SELECT USING (auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can create sources" ON sources
  FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can view search queries" ON search_queries
  FOR SELECT USING (auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can create search queries" ON search_queries
  FOR INSERT WITH CHECK (auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can view own file uploads" ON file_uploads
  FOR SELECT USING (user_id = auth.uid() OR auth.role() IN ('anon', 'service_role'));

CREATE POLICY "Users can create own file uploads" ON file_uploads
  FOR INSERT WITH CHECK (user_id = auth.uid() OR auth.role() IN ('anon', 'service_role'));;