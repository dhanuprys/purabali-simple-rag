#!/usr/bin/env python3
"""
Model preloading script for Docker containers
This script downloads and caches the sentence-transformers model
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from model_cache import model_cache, get_cached_model

def main():
    """Preload the model and cache it"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting model preloading...")
    
    try:
        # Get cache info before loading
        cache_info = model_cache.get_cache_info()
        logger.info(f"Cache info: {cache_info}")
        
        if cache_info['is_valid']:
            logger.info("Model cache is valid, loading from cache...")
            model = get_cached_model()
        else:
            logger.info("Model cache is invalid or missing, downloading model...")
            model = get_cached_model()
        
        # Test the model
        test_text = "Test embedding"
        embedding = model.encode(test_text, convert_to_numpy=True, normalize_embeddings=True)
        logger.info(f"Model test successful. Embedding shape: {embedding.shape}")
        
        # Get final cache info
        final_cache_info = model_cache.get_cache_info()
        cache_size_mb = final_cache_info['size_bytes'] / (1024 * 1024)
        logger.info(f"Model cached successfully. Cache size: {cache_size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to preload model: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 