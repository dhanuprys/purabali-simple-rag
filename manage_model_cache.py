#!/usr/bin/env python3
"""
Model cache management script
This script helps manage the sentence-transformers model cache
"""

import os
import sys
import argparse
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.model_cache import model_cache, get_cached_model

def download_model():
    """Download and cache the model"""
    print("Downloading and caching model...")
    try:
        model = get_cached_model()
        cache_info = model_cache.get_cache_info()
        cache_size_mb = cache_info['size_bytes'] / (1024 * 1024)
        print(f"✅ Model downloaded and cached successfully!")
        print(f"📁 Cache location: {cache_info['cache_path']}")
        print(f"📊 Cache size: {cache_size_mb:.2f} MB")
        return True
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False

def clear_cache():
    """Clear the model cache"""
    print("Clearing model cache...")
    try:
        success = model_cache.clear_cache()
        if success:
            print("✅ Model cache cleared successfully!")
            return True
        else:
            print("❌ Failed to clear model cache")
            return False
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False

def show_info():
    """Show cache information"""
    cache_info = model_cache.get_cache_info()
    print("📋 Model Cache Information:")
    print(f"   Model: {cache_info['model_name']}")
    print(f"   Cache Directory: {cache_info['cache_dir']}")
    print(f"   Cache Path: {cache_info['cache_path']}")
    print(f"   Exists: {'✅ Yes' if cache_info['exists'] else '❌ No'}")
    print(f"   Valid: {'✅ Yes' if cache_info['is_valid'] else '❌ No'}")
    
    if cache_info['exists']:
        cache_size_mb = cache_info['size_bytes'] / (1024 * 1024)
        print(f"   Size: {cache_size_mb:.2f} MB")
    
    # Check if local model_storage directory exists
    local_storage = Path("./model_storage")
    print(f"\n📁 Local Storage Directory:")
    print(f"   Path: {local_storage.absolute()}")
    print(f"   Exists: {'✅ Yes' if local_storage.exists() else '❌ No'}")
    
    if local_storage.exists():
        total_size = sum(f.stat().st_size for f in local_storage.rglob('*') if f.is_file())
        total_size_mb = total_size / (1024 * 1024)
        print(f"   Total Size: {total_size_mb:.2f} MB")

def test_model():
    """Test the cached model"""
    print("Testing cached model...")
    try:
        model = get_cached_model()
        test_text = "Test embedding for model validation"
        embedding = model.encode(test_text, convert_to_numpy=True, normalize_embeddings=True)
        print(f"✅ Model test successful!")
        print(f"   Input: '{test_text}'")
        print(f"   Output shape: {embedding.shape}")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Manage sentence-transformers model cache")
    parser.add_argument("action", choices=["download", "clear", "info", "test"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "download":
        download_model()
    elif args.action == "clear":
        clear_cache()
    elif args.action == "info":
        show_info()
    elif args.action == "test":
        test_model()

if __name__ == "__main__":
    main() 