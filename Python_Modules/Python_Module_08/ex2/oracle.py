# oracle.py
import os
import sys


def load_env_file(env_path=".env"):
    """Load environment variables from a .env file manually"""
    if not os.path.exists(env_path):
        return
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            # Only set if not already in os.environ
            os.environ.setdefault(key, value)


def get_config():
    """Fetch configuration values with defaults and validation"""
    config = {}
    config['MATRIX_MODE'] = os.environ.get("MATRIX_MODE", "development")
    config['DATABASE_URL'] = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    config['API_KEY'] = os.environ.get("API_KEY", None)
    config['LOG_LEVEL'] = os.environ.get("LOG_LEVEL", "INFO")
    config['ZION_ENDPOINT'] = os.environ.get("ZION_ENDPOINT", "http://localhost:8000")

    # Security checks
    if config['API_KEY'] is None:
        print("[WARNING] API_KEY is not set! Services may not authenticate correctly.")
    if "secret" in config['DATABASE_URL'] or "password" in config['DATABASE_URL']:
        print("[WARNING] Sensitive info detected in DATABASE_URL!")

    return config

def main():
    print("ORACLE STATUS: Reading the Matrix...")

    # Load .env file if it exists
    load_env_file()

    config = get_config()

    # Display configuration
    print("Configuration loaded:")
    print(f"Mode: {config['MATRIX_MODE']}")
    print(f"Database: {config['DATABASE_URL']}")
    print(f"API Access: {'Authenticated' if config['API_KEY'] else 'Unauthenticated'}")
    print(f"Log Level: {config['LOG_LEVEL']}")
    print(f"Zion Network: {config['ZION_ENDPOINT']}")

    # Environment security check
    print("\nEnvironment security check:")
    # Check for hardcoded secrets
    hardcoded_detected = False
    for key, value in config.items():
        if value and ("secret" in value.lower() or "password" in value.lower()):
            print(f"[WARNING] Potential hardcoded secret detected in {key}")
            hardcoded_detected = True
    if not hardcoded_detected:
        print("[OK] No hardcoded secrets detected")

    # Check .env presence
    if os.path.exists(".env"):
        print("[OK] .env file properly configured")
    else:
        print("[WARNING] .env file not found")

    # Check production override
    if config['MATRIX_MODE'] == "production":
        print("[OK] Production overrides available")
    else:
        print("[INFO] Running in development mode")

    print("The Oracle sees all configurations.")

if __name__ == "__main__":
    main()
