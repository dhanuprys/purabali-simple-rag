#!/usr/bin/env python3
"""
Utility functions for managing Gemini API key rotation
"""

import os
from .config import GeminiConfig

def test_key_rotation():
    """Test the key rotation system"""
    print("=== Gemini API Key Rotation Test ===")
    
    # Display current configuration
    total_keys = GeminiConfig.get_total_keys()
    current_index = GeminiConfig.get_current_key_index()
    
    print(f"Total API keys available: {total_keys}")
    print(f"Current key index: {current_index}")
    
    if total_keys == 0:
        print("❌ No API keys found!")
        print("Please set either GEMINI_API_KEY or GEMINI_API_KEYS environment variables")
        return
    
    # Test rotation
    print("\n--- Testing Key Rotation ---")
    for i in range(min(5, total_keys * 2)):  # Test rotation for 5 requests or 2 full cycles
        key = GeminiConfig.get_next_api_key()
        if key:
            current_idx = GeminiConfig.get_current_key_index()
            print(f"Request {i+1}: Using key at index {current_idx} (first 10 chars: {key[:10]}...)")
        else:
            print(f"Request {i+1}: No key available")
    
    # Reset rotation
    GeminiConfig.reset_rotation()
    print(f"\n--- Reset rotation to index 0 ---")
    
    # Show all keys (first 10 chars only for security)
    print("\n--- All Available Keys ---")
    keys = GeminiConfig.get_api_keys()
    for i, key in enumerate(keys):
        print(f"Key {i}: {key[:10]}...")

def show_key_status():
    """Show current key rotation status"""
    total_keys = GeminiConfig.get_total_keys()
    current_index = GeminiConfig.get_current_key_index()
    
    print(f"Total keys: {total_keys}")
    print(f"Current index: {current_index}")
    
    if total_keys > 0:
        print(f"Next key will be: {current_index + 1 if current_index + 1 < total_keys else 0}")

def get_environment_info():
    """Show environment variable information"""
    print("=== Environment Variables ===")
    
    single_key = os.getenv("GEMINI_API_KEY")
    multiple_keys = os.getenv("GEMINI_API_KEYS")
    
    if single_key:
        print(f"GEMINI_API_KEY: {single_key[:10]}...")
    else:
        print("GEMINI_API_KEY: Not set")
    
    if multiple_keys:
        keys_list = [key.strip() for key in multiple_keys.split(",") if key.strip()]
        print(f"GEMINI_API_KEYS: {len(keys_list)} keys found")
        for i, key in enumerate(keys_list):
            print(f"  Key {i}: {key[:10]}...")
    else:
        print("GEMINI_API_KEYS: Not set")

if __name__ == "__main__":
    print("Gemini API Key Rotation Utility")
    print("=" * 40)
    
    get_environment_info()
    print()
    show_key_status()
    print()
    test_key_rotation() 