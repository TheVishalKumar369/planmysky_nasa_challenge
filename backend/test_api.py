#!/usr/bin/env python3
"""
Quick test script for Weather API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """Test all API endpoints"""
    print("=" * 60)
    print("Testing PlanMySky Weather API")
    print("=" * 60)

    # Test 1: Status
    print("\n1. Testing /api/status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"   Status code: {response.status_code}")
        data = response.json()
        print(f"   Predictor loaded: {data['predictor_loaded']}")
        print(f"   Data years: {data['data_years']}")
        print(f"   Location: {data['location']}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Weather prediction (GET)
    print("\n2. Testing /api/predict/7/15 (July 15)...")
    try:
        response = requests.get(f"{BASE_URL}/api/predict/7/15", params={"window_days": 7})
        print(f"   Status code: {response.status_code}")
        data = response.json()
        print(f"   Rain probability: {data['rainfall']['probability_percent']}%")
        print(f"   Expected rainfall: {data['rainfall']['expected_amount_mm']} mm")
        print(f"   Temperature: {data['temperature']['expected_range']['min']}-{data['temperature']['expected_range']['max']}°C")
        print(f"   Weather: {data['weather_category']}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Weather prediction (POST)
    print("\n3. Testing /api/predict (POST)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/predict",
            json={"month": 1, "day": 15, "window_days": 7}
        )
        print(f"   Status code: {response.status_code}")
        data = response.json()
        print(f"   Rain probability: {data['rainfall']['probability_percent']}%")
        print(f"   Weather: {data['weather_category']}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 4: Monthly statistics
    print("\n4. Testing /api/monthly/7 (July stats)...")
    try:
        response = requests.get(f"{BASE_URL}/api/monthly/7")
        print(f"   Status code: {response.status_code}")
        data = response.json()
        print(f"   Month: {data['month_name']}")
        print(f"   Rainy days: {data['rainfall']['rainy_days_percent']}%")
        print(f"   Avg temp: {data['temperature']['average_mean_celsius']}°C")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 5: Health check
    print("\n5. Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"   Status code: {response.status_code}")
        data = response.json()
        print(f"   Status: {data['status']}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the API server is running:")
    print("  cd backend/api")
    print("  python weather_api.py")
    print()
    input("Press Enter to start tests...")

    test_api()
