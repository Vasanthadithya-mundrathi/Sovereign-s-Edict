# Phase 1: Security Fixes Implementation

## Immediate Actions Required

### 1. Remove Sensitive Data from Git History

#### Step 1: Install BFG Repo-Cleaner
```bash
# Download BFG Repo-Cleaner
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar -O bfg.jar
```

#### Step 2: Backup Current Repository
```bash
# Create a backup of the current repository
cd "/Users/vasanthadithya/SIH 2025"
cp -r "Sovereign's Edict" "Sovereign's Edict.backup"
```

#### Step 3: Remove .env File from History
```bash
# Navigate to the repository
cd "/Users/vasanthadithya/SIH 2025/Sovereign's Edict"

# Remove .env file from all of git history
java -jar ../bfg.jar --delete-files .env

# Clean up the repository
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

#### Step 4: Force Push Cleaned Repository
```bash
# Force push the cleaned history
git push --force-with-lease
```

#### Step 5: Verify Removal
```bash
# Check that .env is no longer in history
git log --all -- .env

# Verify current .env file is not tracked
git status
```

### 2. Rotate Compromised API Key

#### Step 1: Generate New Gemini API Key
1. Go to Google AI Studio: https://aistudio.google.com/
2. Navigate to API Keys section
3. Revoke the compromised key: `AIzaSyAH9JlLvl8TOocBLP_6ndpRmLF-WQP4U94`
4. Generate a new API key
5. Update your `.env` file with the new key

#### Step 2: Update Environment Configuration
```bash
# Update .env file with new API key
echo "GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE" > .env
```

### 3. Enhanced Security Measures

#### Step 1: Implement Input Validation
Add input validation to all API endpoints in `backend/main.py`:

```python
from pydantic import BaseModel, validator
import re

class YouTubeLinkRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_youtube_url(cls, v):
        if not re.match(r'^https?://(www\.)?(youtube\.com|youtu\.?be)/.+', v):
            raise ValueError('Invalid YouTube URL')
        return v

class WebURLRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_web_url(cls, v):
        if not re.match(r'^https?://.+\..+', v):
            raise ValueError('Invalid web URL')
        return v
```

#### Step 2: Add Rate Limiting
Install the required dependency:
```bash
pip install slowapi
```

Add rate limiting to `backend/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_comments(request: Request):
    # Existing analysis code
    pass
```

#### Step 3: Add Comprehensive Logging
Add logging to `backend/main.py`:
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.post("/analyze")
async def analyze_comments():
    logger.info("Analysis request received")
    # Existing analysis code
    logger.info(f"Analysis completed for {len(stored_data['comments'])} comments")
```

## Verification Steps

### 1. Verify Git History Cleanup
```bash
# Check that .env file is completely removed from history
git log --all --full-history -- .env

# Should return no results
```

### 2. Verify API Key Rotation
```bash
# Test that the old API key no longer works
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyAH9JlLvl8TOocBLP_6ndpRmLF-WQP4U94" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'

# Should return an error
```

### 3. Verify New Security Measures
- Test input validation with invalid URLs
- Verify rate limiting works correctly
- Check that logging is capturing events

## Rollback Plan

If any issues occur during the security fixes:

1. Restore from the backup:
```bash
cd "/Users/vasanthadithya/SIH 2025"
rm -rf "Sovereign's Edict"
cp -r "Sovereign's Edict.backup" "Sovereign's Edict"
```

2. Revert to the previous state and try alternative approaches:
```bash
# Alternative approach using git filter-branch
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch .env' \
--prune-empty --tag-name-filter cat -- --all
```

## Next Steps

After completing these security fixes:
1. Proceed to Phase 2: Dynamic Data Ingestion
2. Update documentation to reflect security improvements
3. Notify team members about the security updates
4. Schedule regular security audits