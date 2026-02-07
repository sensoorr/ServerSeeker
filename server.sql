-- Server.sql file provided from https://github.com/fuuuuuuuuuuuuuuck/ServerSeekerV2-guide by fuuuuuuuuuuuuuuck

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'software') THEN
        CREATE TYPE software AS ENUM (
            'Java', 'Neoforge', 'Lexforge', 'Paper', 'Spigot', 'Bukkit', 
            'Purpur', 'Folia', 'Pufferfish', 'Velocity', 'Leaves', 
            'Waterfall', 'Bungeecord', 'Thermos'
        );
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS servers (
    address CIDR NOT NULL,
    port INTEGER NOT NULL,
    software software NOT NULL,
    version TEXT,
    protocol INTEGER,
    icon TEXT,
    description_raw JSONB,
    description_formatted TEXT,
    prevents_chat_reports BOOLEAN,
    enforces_secure_chat BOOLEAN,
    first_seen INTEGER NOT NULL,
    last_seen INTEGER NOT NULL,
    online_players INTEGER,
    max_players INTEGER,
    country VARCHAR(2),
    asn VARCHAR(16),
    PRIMARY KEY (address, port)
);

CREATE TABLE IF NOT EXISTS mods (
    address CIDR NOT NULL,
    port INTEGER NOT NULL,
    id TEXT NOT NULL,
    mod_marker TEXT,
    PRIMARY KEY (address, port, id)
);

CREATE TABLE IF NOT EXISTS countries (
    network CIDR PRIMARY KEY,
    country VARCHAR(255),
    country_code VARCHAR(2),
    asn VARCHAR(16),
    company VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS countries_table_index ON countries USING GIST (network inet_ops);