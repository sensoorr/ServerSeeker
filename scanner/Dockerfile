FROM rustlang/rust:nightly-slim as builder
WORKDIR /app

RUN apt-get update && apt-get install -y pkg-config libssl-dev libpq-dev && rm -rf /var/lib/apt/lists/*

COPY . .

RUN cargo build --release

FROM debian:trixie-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    ca-certificates \
    sudo \
    masscan \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/ServerScanner /app/scanner

COPY config.toml ./config.toml
COPY masscan.conf ./masscan.conf

CMD ["./scanner", "--mode", "discovery"]