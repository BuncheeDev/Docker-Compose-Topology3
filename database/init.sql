-- ============================================================================
-- Topology Database Schema
-- ============================================================================

-- Create hosts table
CREATE TABLE IF NOT EXISTS hosts (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(15) UNIQUE NOT NULL,
    mac_address VARCHAR(17),
    hostname VARCHAR(255),
    device_type VARCHAR(50),
    glyph VARCHAR(10),
    is_gateway BOOLEAN DEFAULT FALSE,
    is_self BOOLEAN DEFAULT FALSE,
    online BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scan results table
CREATE TABLE IF NOT EXISTS scan_results (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(50) UNIQUE NOT NULL,
    subnet VARCHAR(30),
    gateway_ip VARCHAR(15),
    self_ip VARCHAR(15),
    total_hosts INT,
    online_hosts INT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scan_hosts junction table
CREATE TABLE IF NOT EXISTS scan_hosts (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(50),
    host_id INT,
    latency_ms FLOAT,
    status VARCHAR(20),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id),
    UNIQUE(scan_id, host_id)
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    from_host VARCHAR(255),
    to_ip VARCHAR(15),
    message_text TEXT,
    method VARCHAR(50),
    status VARCHAR(20),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create action history table
CREATE TABLE IF NOT EXISTS action_history (
    id SERIAL PRIMARY KEY,
    host_ip VARCHAR(15),
    action_type VARCHAR(50),
    action_data JSONB,
    result JSONB,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for better query performance
CREATE INDEX IF NOT EXISTS idx_hosts_ip ON hosts(ip_address);
CREATE INDEX IF NOT EXISTS idx_hosts_mac ON hosts(mac_address);
CREATE INDEX IF NOT EXISTS idx_hosts_online ON hosts(online);
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id);
CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);
CREATE INDEX IF NOT EXISTS idx_action_history_ip ON action_history(host_ip);
