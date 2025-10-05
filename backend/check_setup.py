#!/usr/bin/env python3
"""
Quick diagnostic script to check PlanMySky setup
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("PlanMySky Setup Diagnostic")
print("=" * 60)
print()

# Check if we're in the right directory
backend_dir = Path(__file__).parent
print(f"✓ Backend directory: {backend_dir}")
print()

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = backend_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print("✓ .env file found and loaded")
    else:
        print("✗ .env file NOT found!")
        print(f"  Expected at: {env_file}")
except ImportError:
    print("⚠ python-dotenv not installed")
    print("  Run: pip install python-dotenv")

print()

# Check Google OAuth configuration
print("Google OAuth Configuration:")
print("-" * 40)
client_id = os.getenv("GOOGLE_CLIENT_ID", "")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "")

if client_id:
    print(f"✓ CLIENT_ID: {client_id[:30]}...")
else:
    print("✗ CLIENT_ID: NOT SET")

if client_secret:
    print(f"✓ CLIENT_SECRET: {client_secret[:15]}...")
else:
    print("✗ CLIENT_SECRET: NOT SET")

if redirect_uri:
    print(f"✓ REDIRECT_URI: {redirect_uri}")
else:
    print("✗ REDIRECT_URI: NOT SET")

print()

# Check required packages
print("Required Python Packages:")
print("-" * 40)

packages = {
    'fastapi': 'FastAPI framework',
    'uvicorn': 'ASGI server',
    'httpx': 'HTTP client for OAuth',
    'python-dotenv': 'Environment variables',
    'pandas': 'Data processing',
    'numpy': 'Numerical computing'
}

missing_packages = []

for package, description in packages.items():
    try:
        __import__(package.replace('-', '_'))
        print(f"✓ {package:20s} - {description}")
    except ImportError:
        print(f"✗ {package:20s} - {description} (NOT INSTALLED)")
        missing_packages.append(package)

print()

if missing_packages:
    print("Missing packages. Install with:")
    print(f"  pip install {' '.join(missing_packages)}")
    print()

# Check data directories
print("Data Directories:")
print("-" * 40)

data_dirs = [
    backend_dir.parent / "data" / "raw",
    backend_dir.parent / "data" / "processed",
    backend_dir.parent / "data" / "tokens",
]

for data_dir in data_dirs:
    if data_dir.exists():
        print(f"✓ {data_dir.relative_to(backend_dir.parent)}")
    else:
        print(f"⚠ {data_dir.relative_to(backend_dir.parent)} (will be created)")

print()

# Summary
print("=" * 60)
print("Setup Summary:")
print("=" * 60)

issues = []

if not client_id or not client_secret:
    issues.append("Configure Google OAuth credentials in .env")

if missing_packages:
    issues.append(f"Install missing packages: {', '.join(missing_packages)}")

if issues:
    print("⚠ Issues found:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("✓ All checks passed! Ready to run.")

print()
print("To start the backend server:")
print("  cd backend/api")
print("  python weather_api.py")
print()
print("=" * 60)
