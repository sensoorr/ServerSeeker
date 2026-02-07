#![feature(string_from_utf8_lossy_owned)]

mod config;
mod country_tracking;
mod database;
mod protocol;
mod response;
mod scanner;
mod utils;

use crate::scanner::Scanner;
use clap::Parser;
use config::load_config;
use scanner::Mode;
use sqlx::postgres::{PgConnectOptions, PgPoolOptions};
use sqlx::ConnectOptions;
use std::time::Duration;
use tracing::log::LevelFilter;
use tracing::{error, info};
use std::env;

#[derive(Parser, Debug)]
#[clap(about = "Scans the internet for minecraft servers and indexes them")]
#[clap(rename_all = "kebab-case")]
struct Args {
    #[clap(help = "Specifies the mode to run")]
    #[clap(default_value = "discovery")]
    #[clap(long, short = 'm')]
    mode: Mode,

    #[clap(help = "Specifies the location of the config file")]
    #[clap(default_value = "config.toml")]
    #[clap(long, short = 'c')]
    config_file: String,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let arguments = Args::parse();
    let config = match load_config(&arguments.config_file) {
        Ok(config) => config,
        Err(e) => {
            error!("Fatal error loading config file: {}", e);
            std::process::exit(1);
        }
    };

    info!("Using config file: {}", arguments.config_file);

    let options = match env::var("DB_URL") {
        Ok(url) => {
            info!("Using database URL from environment variable");
            url.parse::<PgConnectOptions>()
                .expect("Failed to parse DB_URL from environment")
        }
        Err(_) => {
            info!("DB_URL not set, using database settings from config file");
            PgConnectOptions::new()
                .username(&config.database.user)
                .password(&config.database.password)
                .host(&config.database.host)
                .port(config.database.port)
                .database(&config.database.table)
        }
    }
    .log_slow_statements(LevelFilter::Off, Duration::from_secs(60));

    let pool = PgPoolOptions::new()
        .max_lifetime(Duration::from_secs(86400))
        .acquire_slow_threshold(Duration::from_secs(60))
        .connect_with(options)
        .await
        .ok();

    let pool = match pool {
        Some(p) => p,
        None => {
            error!("Failed to connect to database");
            std::process::exit(1);
        }
    };

    // --- CRITICAL FIX: Ensure Country Tracking is ready before Scanner starts ---
    if config.country_tracking.enabled {
        let pool_clone = pool.clone();
        let config_clone = config.clone();
        
        info!("Ensuring country database is ready...");
        if let Err(e) = country_tracking::create_tables(&pool_clone).await {
            error!("Failed to create country tables: {}", e);
            std::process::exit(1);
        }

        // Run the first check/download synchronously to prevent "no rows" errors
        if let Err(e) = country_tracking::country_tracking(pool_clone.clone(), config_clone.clone()).await {
             error!("Initial country tracking sync failed: {}", e);
        }

        // Now spawn the loop in the background for future updates
        tokio::task::spawn(async move {
            loop {
                tokio::time::sleep(Duration::from_secs(config_clone.country_tracking.update_frequency * 3600)).await;
                if let Err(e) = country_tracking::country_tracking(pool_clone.clone(), config_clone.clone()).await {
                    error!("Background country tracking update failed: {}", e);
                }
            }
        });
    }

    info!("Starting Scanner in {:?} mode...", arguments.mode);
    Scanner::new()
        .config(config)
        .mode(arguments.mode)
        .pool(Some(pool))
        .build()
        .start()
        .await;
}