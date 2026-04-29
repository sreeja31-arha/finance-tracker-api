# app/logging_config.py

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """
    Sets up logging for the Flask app.
    Called once in create_app() in app/__init__.py
    """

    # ── 1. Read LOG_LEVEL from config (set in .env) ───────────────────────
    # getattr safely converts "DEBUG" string → logging.DEBUG integer
    # Falls back to logging.INFO if LOG_LEVEL is missing or invalid
    log_level = getattr(
        logging,
        app.config.get("LOG_LEVEL", "INFO").upper(),
        logging.INFO
    )

    # ── 2. Define how each log line looks ────────────────────────────────
    # Output example:
    # [2024-01-15 10:23:45] INFO     in auth: User logged in — id: 1
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s in %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # %(levelname)-8s pads level names to 8 chars so columns stay aligned:
    # INFO     ← 8 chars
    # WARNING  ← 8 chars
    # DEBUG    ← 8 chars

    # ── 3. Handler 1: Console (prints to terminal) ────────────────────────
    # You'll see INFO+ messages in your terminal when the server runs.
    # DEBUG messages are too noisy for the terminal — they go to file only.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)   # Terminal: INFO and above only

    # ── 4. Handler 2: RotatingFileHandler (writes to logs/app.log) ────────
    # Creates the logs/ folder if it doesn't exist yet
    os.makedirs("logs", exist_ok=True)

    # maxBytes=5_000_000 → rotate after 5MB
    # backupCount=3 → keep app.log.1, app.log.2, app.log.3 as backups
    # encoding="utf-8" → handles special characters safely
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)   # File: captures EVERYTHING (DEBUG+)

    # ── 5. Configure Flask's built-in logger (app.logger) ─────────────────
    # Flask's default level is WARNING — we override it here
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    # ── 6. Configure the ROOT logger ──────────────────────────────────────
    # CRITICAL: app.logger only catches Flask's own internal messages.
    # Your files (auth.py, routes.py) use logging.getLogger(__name__) which
    # goes through the ROOT logger — so we configure that too.
    # Both loggers share the same handlers → same file, same terminal output.
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # ── 7. Silence noisy third-party libraries ────────────────────────────
    # SQLAlchemy logs every SQL query at DEBUG → very spammy
    # Werkzeug logs every HTTP request at INFO → clutters terminal
    # We raise their floor to WARNING so they only appear if something breaks
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    # ── 8. Confirm logging is ready ───────────────────────────────────────
    app.logger.info(
        "Logging configured — level: %s | terminal: INFO+ | file: DEBUG+ → logs/app.log",
        app.config.get("LOG_LEVEL", "INFO")
    )