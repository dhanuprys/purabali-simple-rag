# Gemini API Key Rotation System

This system allows you to use multiple Gemini API keys and rotate through them sequentially for each request, helping to distribute load and avoid rate limits.

## Features

- **Sequential Rotation**: Keys are used in order, one per request
- **Thread-Safe**: Uses locks to ensure thread safety in multi-threaded environments
- **Fallback Support**: Supports both single key and multiple keys
- **Environment Variables**: Keys are stored securely in environment variables
- **Utility Functions**: Helper functions to test and manage the rotation system

## Setup

### Option 1: Single API Key (Backward Compatible)
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### Option 2: Multiple API Keys (Recommended)
```bash
export GEMINI_API_KEYS="key1,key2,key3,key4"
```

You can add as many keys as you want, separated by commas. The system will automatically rotate through them.

## Usage

The system is automatically integrated into your existing code. The `generate_response()` function in `app/gen.py` now uses the key rotation system.

### Key Rotation Methods

```python
from app.config import GeminiConfig

# Get the next key in rotation
api_key = GeminiConfig.get_next_api_key()

# Get a random key
api_key = GeminiConfig.get_random_api_key()

# Get all available keys
keys = GeminiConfig.get_api_keys()

# Get current rotation status
current_index = GeminiConfig.get_current_key_index()
total_keys = GeminiConfig.get_total_keys()

# Reset rotation to start from first key
GeminiConfig.reset_rotation()
```

## Testing the System

Run the utility script to test your key rotation setup:

```bash
cd app
python -c "from gemini_utils import test_key_rotation, show_key_status, get_environment_info; get_environment_info(); print(); show_key_status(); print(); test_key_rotation()"
```

Or run it as a module:

```bash
python -m app.gemini_utils
```

## How It Works

1. **Loading Keys**: The system loads API keys from environment variables on first use
2. **Sequential Rotation**: Each request gets the next key in the sequence
3. **Thread Safety**: Uses locks to prevent race conditions in multi-threaded environments
4. **Automatic Wrapping**: When reaching the last key, it wraps back to the first key
5. **Error Handling**: Provides clear error messages if no keys are available

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Single API key (legacy support) | `AIzaSyC...` |
| `GEMINI_API_KEYS` | Multiple API keys (comma-separated) | `key1,key2,key3` |

## Benefits

- **Load Distribution**: Spreads requests across multiple API keys
- **Rate Limit Management**: Reduces the chance of hitting rate limits
- **High Availability**: If one key fails, others continue working
- **Cost Management**: Distribute costs across multiple accounts if needed

## Example .env File

```env
# Single key (legacy)
GEMINI_API_KEY=your-single-api-key

# OR Multiple keys (recommended)
GEMINI_API_KEYS=key1,key2,key3,key4,key5
```

## Monitoring

You can monitor key usage by checking the current index:

```python
from app.config import GeminiConfig

print(f"Current key index: {GeminiConfig.get_current_key_index()}")
print(f"Total keys: {GeminiConfig.get_total_keys()}")
```

## Troubleshooting

### No Keys Available
If you get "No Gemini API keys available" error:
1. Check that `GEMINI_API_KEY` or `GEMINI_API_KEYS` is set
2. Verify the keys are valid
3. Make sure there are no extra spaces in the comma-separated list

### Key Rotation Not Working
1. Check that multiple keys are properly comma-separated
2. Verify the keys are different (not duplicates)
3. Use the test utility to verify rotation is working

### Performance Issues
- The system is designed to be lightweight
- Key rotation happens only when `get_next_api_key()` is called
- Keys are cached in memory after first load 