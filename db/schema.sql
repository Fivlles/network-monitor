CREATE TABLE devices (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45)  NOT NULL,
    port       INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE checks (
    id          SERIAL PRIMARY KEY,
    device_id   INTEGER NOT NULL REFERENCES devices(id),
    checked_at  TIMESTAMP DEFAULT NOW(),
    is_up       BOOLEAN NOT NULL,
    latency_ms  REAL
);

CREATE INDEX idx_checks_device_time ON checks (device_id, checked_at);

INSERT INTO devices (name, ip_address, port) VALUES
    ('Google DNS',     '8.8.8.8',     53),
    ('Cloudflare DNS', '1.1.1.1',     53),
    ('Google Website', 'google.com',  443),
    ('Home Router',    '192.168.1.1', 80);