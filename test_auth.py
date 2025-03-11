#!/usr/bin/env python

import argparse
import requests
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Test API authentication")
    parser.add_argument("--url", default="http://localhost:15432", help="API base URL")
    parser.add_argument("--key", default="invalid-key", help="API key to test")
    parser.add_argument("--debug", action="store_true", help="Query debug endpoint")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    args = parser.parse_args()

    # Get the debug info first to understand the server config
    try:
        response = requests.get(f"{args.url}/debug/auth")
        if args.verbose:
            print(f"Server auth config: {json.dumps(response.json(), indent=2)}")
        config = response.json()
        if config.get("auth_enabled"):
            print(f"Auth is ENABLED with {config.get('api_keys_count')} keys configured")
            print(f"Expected keys: {config.get('api_keys_sample')}")
            print(f"Raw env value: {config.get('raw_env_value')}")
        else:
            print("Auth is DISABLED - any key will be accepted")
    except Exception as e:
        print(f"Failed to get auth config: {e}")
    
    # Header format: Bearer sk-xxx
    headers = {"Authorization": f"Bearer {args.key}"} if args.key else {}
    print(f"\nTesting with API key: {args.key or '(none)'}")
    
    try:
        # Test models endpoint
        response = requests.get(f"{args.url}/models", headers=headers)
        print(f"Models API status: {response.status_code}")
        
        if response.status_code == 200:
            print("\033[92mAPI key was ACCEPTED ✓\033[0m")
        elif response.status_code == 401:
            print("\033[91mAPI key was REJECTED ✗\033[0m")
            print(f"Error: {response.json().get('detail', 'Unknown error')}")
        else:
            print(f"Unexpected response: {response.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
