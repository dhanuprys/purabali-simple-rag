import os
import pickle
import logging
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ModelCache:
    """Model caching system for sentence-transformers models"""
    
    def __init__(self, cache_dir: str = ""):
        # Use environment variable or default to a separate storage location
        if not cache_dir:
            cache_dir = os.getenv("MODEL_CACHE_DIR", "./models")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_name = "intfloat/multilingual-e5-large"
        self.model_cache_path = self.cache_dir / f"{self.model_name.replace('/', '_')}.pkl"
        
    def _get_model_info(self) -> dict:
        """Get model information for cache validation"""
        return {
            "model_name": self.model_name,
            "cache_version": "1.0"
        }
    
    def _is_cache_valid(self) -> bool:
        """Check if the cached model is valid"""
        if not self.model_cache_path.exists():
            return False
            
        try:
            with open(self.cache_dir / "model_info.pkl", "rb") as f:
                cached_info = pickle.load(f)
            current_info = self._get_model_info()
            return cached_info == current_info
        except Exception as e:
            logger.warning(f"Failed to validate cache: {e}")
            return False
    
    def load_model(self) -> SentenceTransformer:
        """Load model from cache or download if not cached"""
        if self._is_cache_valid():
            logger.info("Loading model from cache...")
            try:
                with open(self.model_cache_path, "rb") as f:
                    model = pickle.load(f)
                logger.info("Model loaded successfully from cache")
                return model
            except Exception as e:
                logger.warning(f"Failed to load from cache: {e}")
        
        logger.info("Downloading and caching model...")
        model = SentenceTransformer(self.model_name)
        
        # Cache the model
        try:
            with open(self.model_cache_path, "wb") as f:
                pickle.dump(model, f)
            
            # Save model info
            with open(self.cache_dir / "model_info.pkl", "wb") as f:
                pickle.dump(self._get_model_info(), f)
                
            logger.info(f"Model cached successfully at {self.model_cache_path}")
        except Exception as e:
            logger.warning(f"Failed to cache model: {e}")
        
        return model
    
    def clear_cache(self) -> bool:
        """Clear the model cache"""
        try:
            if self.model_cache_path.exists():
                self.model_cache_path.unlink()
            if (self.cache_dir / "model_info.pkl").exists():
                (self.cache_dir / "model_info.pkl").unlink()
            logger.info("Model cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_size(self) -> int:
        """Get the size of the cached model in bytes"""
        if self.model_cache_path.exists():
            return self.model_cache_path.stat().st_size
        return 0
    
    def get_cache_info(self) -> dict:
        """Get information about the cache"""
        return {
            "cache_dir": str(self.cache_dir),
            "model_name": self.model_name,
            "cache_path": str(self.model_cache_path),
            "exists": self.model_cache_path.exists(),
            "size_bytes": self.get_cache_size(),
            "is_valid": self._is_cache_valid()
        }

# Global model cache instance
model_cache = ModelCache()

def get_cached_model() -> SentenceTransformer:
    """Get the cached sentence-transformers model"""
    return model_cache.load_model() 