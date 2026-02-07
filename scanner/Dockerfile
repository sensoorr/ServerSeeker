# --- Stage 1: Build ---
FROM rustlang/rust:nightly-slim as builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y pkg-config libssl-dev libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the scanner source code
COPY . .

# Build the release binary
RUN cargo build --release

# --- Stage 2: Runtime ---
FROM debian:trixie-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    ca-certificates \
    sudo \
    masscan \
    && rm -rf /var/lib/apt/lists/*

# Copy the binary from the builder
COPY --from=builder /app/target/release/ServerScanner /app/scanner

# CHANGE THIS LINE: Copy your real config instead of the example
COPY config.toml ./config.toml
# Ensure masscan.conf is also copied if it's in the scanner folder
COPY masscan.conf ./masscan.conf

# Run the scanner
CMD ["./scanner", "--mode", "discovery"]