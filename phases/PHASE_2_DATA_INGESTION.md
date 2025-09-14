# Phase 2: Dynamic Data Ingestion Implementation

## Overview
Implement "Smart Ingest" buttons to allow users to paste YouTube links, web URLs, or upload files directly through the dashboard.

## Required Libraries
All libraries are free and don't require API keys:
- `yt-dlp` for YouTube transcript extraction
- `newspaper3k` for web article processing
- `snscrape` for Twitter/X data
- Built-in libraries for CSV/Excel processing

## Implementation Steps

### 1. Backend Implementation

#### Step 1: Install Required Dependencies
Add to `requirements.txt`:
```
yt-dlp>=2023.3.4
newspaper3k>=0.2.8
snscrape>=0.6.2
openpyxl>=3.0.10
```

Install dependencies:
```bash
pip install -r requirements.txt
```

#### Step 2: Create Ingestion Modules

Create `backend/ingestion/youtube_ingestor.py`:
```python
"""
YouTube transcript ingestion for Sovereign's Edict
"""
import yt_dlp
import json
from typing import List
from ..models.comment import Comment
import uuid

def extract_youtube_transcript(url: str) -> List[Comment]:
    """
    Extract transcript from YouTube video and convert to comments
    """
    try:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'json3',
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract transcript if available
            subtitles = info.get('automatic_captions', {}) or info.get('subtitles', {})
            
            if not subtitles:
                raise Exception("No subtitles available for this video")
            
            # Get English subtitles if available
            en_subtitles = subtitles.get('en', []) or subtitles.get('en-US', [])
            
            if not en_subtitles:
                # Try any available subtitles
                en_subtitles = list(subtitles.values())[0] if subtitles else []
            
            if not en_subtitles:
                raise Exception("No English subtitles available")
            
            # Extract text from subtitles
            comments = []
            for subtitle in en_subtitles:
                if subtitle.get('ext') == 'json3':
                    # Parse JSON3 format
                    transcript_data = ydl.urlopen(subtitle['url']).read().decode('utf-8')
                    transcript_json = json.loads(transcript_data)
                    
                    for event in transcript_json.get('events', []):
                        if 'segs' in event:
                            text = ''.join(seg.get('utf8', '') for seg in event['segs'])
                            if text.strip():
                                comment = Comment(
                                    id=str(uuid.uuid4()),
                                    text=text.strip(),
                                    source=url,
                                    timestamp=event.get('tStartMs', 0) / 1000,
                                    policy_clause="youtube_transcript"
                                )
                                comments.append(comment)
                    break
            
            return comments
            
    except Exception as e:
        raise Exception(f"Failed to extract YouTube transcript: {str(e)}")

def get_video_info(url: str) -> dict:
    """
    Get basic information about YouTube video
    """
    try:
        with yt_dlp.YoutubeDL({'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', ''),
                'uploader': info.get('uploader', ''),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', '')
            }
    except Exception as e:
        raise Exception(f"Failed to get video info: {str(e)}")
```

Create `backend/ingestion/web_ingestor.py`:
```python
"""
Web article ingestion for Sovereign's Edict
"""
from newspaper import Article
from typing import List
from ..models.comment import Comment
import uuid

def extract_web_article(url: str) -> List[Comment]:
    """
    Extract article content from web URL and convert to comments
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Split article into paragraphs as separate comments
        paragraphs = article.text.split('\n\n')
        comments = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip() and len(paragraph.strip()) > 20:  # Filter out very short paragraphs
                comment = Comment(
                    id=str(uuid.uuid4()),
                    text=paragraph.strip(),
                    source=url,
                    timestamp=i,
                    policy_clause="web_article"
                )
                comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to extract web article: {str(e)}")

def get_article_info(url: str) -> dict:
    """
    Get basic information about web article
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        return {
            'title': article.title,
            'authors': article.authors,
            'publish_date': article.publish_date,
            'top_image': article.top_image,
            'summary': article.summary[:200] + "..." if len(article.summary) > 200 else article.summary
        }
    except Exception as e:
        raise Exception(f"Failed to get article info: {str(e)}")
```

Create `backend/ingestion/twitter_ingestor.py`:
```python
"""
Twitter/X data ingestion for Sovereign's Edict
"""
import snscrape.modules.twitter as sntwitter
from typing import List
from ..models.comment import Comment
import uuid

def extract_twitter_data(query: str, limit: int = 100) -> List[Comment]:
    """
    Extract tweets based on query and convert to comments
    """
    try:
        comments = []
        scraper = sntwitter.TwitterSearchScraper(query)
        
        for i, tweet in enumerate(scraper.get_items()):
            if i >= limit:
                break
                
            comment = Comment(
                id=str(uuid.uuid4()),
                text=tweet.rawContent,
                source=f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                timestamp=tweet.date.timestamp(),
                policy_clause="twitter_search"
            )
            comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to extract Twitter data: {str(e)}")

def get_twitter_user_tweets(username: str, limit: int = 100) -> List[Comment]:
    """
    Extract tweets from a specific user
    """
    try:
        comments = []
        scraper = sntwitter.TwitterUserScraper(username)
        
        for i, tweet in enumerate(scraper.get_items()):
            if i >= limit:
                break
                
            comment = Comment(
                id=str(uuid.uuid4()),
                text=tweet.rawContent,
                source=f"https://twitter.com/{tweet.user.username}/status/{tweet.id}",
                timestamp=tweet.date.timestamp(),
                policy_clause="twitter_user"
            )
            comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to extract user tweets: {str(e)}")
```

Create `backend/ingestion/file_ingestor.py`:
```python
"""
File ingestion for Sovereign's Edict
"""
import pandas as pd
import json
from typing import List
from ..models.comment import Comment
import uuid

def extract_csv_data(file_path: str) -> List[Comment]:
    """
    Extract comments from CSV file
    """
    try:
        df = pd.read_csv(file_path)
        
        # Check for required columns
        required_columns = ['text']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise Exception(f"Missing required columns: {missing_columns}")
        
        comments = []
        for index, row in df.iterrows():
            comment = Comment(
                id=str(uuid.uuid4()),
                text=str(row['text']),
                source=row.get('source', 'csv_upload'),
                timestamp=row.get('timestamp', index),
                policy_clause=row.get('policy_clause', 'csv_upload')
            )
            comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to extract CSV data: {str(e)}")

def extract_excel_data(file_path: str) -> List[Comment]:
    """
    Extract comments from Excel file
    """
    try:
        df = pd.read_excel(file_path)
        
        # Check for required columns
        required_columns = ['text']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise Exception(f"Missing required columns: {missing_columns}")
        
        comments = []
        for index, row in df.iterrows():
            comment = Comment(
                id=str(uuid.uuid4()),
                text=str(row['text']),
                source=row.get('source', 'excel_upload'),
                timestamp=row.get('timestamp', index),
                policy_clause=row.get('policy_clause', 'excel_upload')
            )
            comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to extract Excel data: {str(e)}")

def extract_json_data(file_path: str) -> List[Comment]:
    """
    Extract comments from JSON file
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        comments = []
        for item in data:
            comment = Comment(
                id=str(uuid.uuid4()),
                text=str(item.get('text', '')),
                source=item.get('source', 'json_upload'),
                timestamp=item.get('timestamp', len(comments)),
                policy_clause=item.get('policy_clause', 'json_upload')
            )
            comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to extract JSON data: {str(e)}")
```

#### Step 3: Update Main API Endpoints

Update `backend/main.py` with new ingestion endpoints:

```python
# Add new imports at the top
from .ingestion.youtube_ingestor import extract_youtube_transcript, get_video_info
from .ingestion.web_ingestor import extract_web_article, get_article_info
from .ingestion.twitter_ingestor import extract_twitter_data, get_twitter_user_tweets
from .ingestion.file_ingestor import extract_csv_data, extract_excel_data, extract_json_data

# Add new endpoints after existing upload endpoints

@app.post("/ingest/youtube")
async def ingest_youtube(url: str):
    """
    Ingest YouTube video transcript
    """
    try:
        # Get video info
        video_info = get_video_info(url)
        
        # Extract transcript
        comments = extract_youtube_transcript(url)
        stored_data["comments"].extend(comments)
        
        return {
            "message": f"Successfully ingested {len(comments)} comments from YouTube video",
            "video_info": video_info,
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ingest/web")
async def ingest_web(url: str):
    """
    Ingest web article
    """
    try:
        # Get article info
        article_info = get_article_info(url)
        
        # Extract article content
        comments = extract_web_article(url)
        stored_data["comments"].extend(comments)
        
        return {
            "message": f"Successfully ingested {len(comments)} comments from web article",
            "article_info": article_info,
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ingest/twitter/search")
async def ingest_twitter_search(query: str, limit: int = 100):
    """
    Ingest tweets based on search query
    """
    try:
        comments = extract_twitter_data(query, limit)
        stored_data["comments"].extend(comments)
        
        return {
            "message": f"Successfully ingested {len(comments)} comments from Twitter search",
            "query": query,
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ingest/twitter/user")
async def ingest_twitter_user(username: str, limit: int = 100):
    """
    Ingest tweets from specific user
    """
    try:
        comments = get_twitter_user_tweets(username, limit)
        stored_data["comments"].extend(comments)
        
        return {
            "message": f"Successfully ingested {len(comments)} comments from Twitter user @{username}",
            "username": username,
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    """
    Ingest data from uploaded file (CSV, Excel, JSON)
    """
    try:
        # Save file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        temp_file_path = f"/tmp/{uuid.uuid4()}.{file_extension}"
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process based on file type
        if file_extension == 'csv':
            comments = extract_csv_data(temp_file_path)
        elif file_extension in ['xlsx', 'xls']:
            comments = extract_excel_data(temp_file_path)
        elif file_extension == 'json':
            comments = extract_json_data(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        stored_data["comments"].extend(comments)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": f"Successfully ingested {len(comments)} comments from {file.filename}",
            "file_type": file_extension,
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Frontend Implementation

#### Step 1: Update UploadTab Component

Update `frontend/src/App.js` UploadTab component:

```javascript
function UploadTab() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [webUrl, setWebUrl] = useState('');
  const [twitterQuery, setTwitterQuery] = useState('');
  const [twitterUser, setTwitterUser] = useState('');
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleYouTubeIngest = async () => {
    if (!youtubeUrl) {
      alert('Please enter a YouTube URL');
      return;
    }
    
    try {
      setUploadStatus('Ingesting YouTube transcript...');
      const response = await fetch('http://localhost:8000/ingest/youtube?url=' + encodeURIComponent(youtubeUrl), {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setUploadStatus(`Success! Ingested ${data.comment_ids.length} comments from "${data.video_info.title}"`);
    } catch (error) {
      setUploadStatus('Error: ' + error.message);
    }
  };

  const handleWebIngest = async () => {
    if (!webUrl) {
      alert('Please enter a web URL');
      return;
    }
    
    try {
      setUploadStatus('Ingesting web article...');
      const response = await fetch('http://localhost:8000/ingest/web?url=' + encodeURIComponent(webUrl), {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setUploadStatus(`Success! Ingested ${data.comment_ids.length} comments from web article`);
    } catch (error) {
      setUploadStatus('Error: ' + error.message);
    }
  };

  const handleTwitterSearchIngest = async () => {
    if (!twitterQuery) {
      alert('Please enter a Twitter search query');
      return;
    }
    
    try {
      setUploadStatus('Ingesting Twitter data...');
      const response = await fetch(`http://localhost:8000/ingest/twitter/search?query=${encodeURIComponent(twitterQuery)}&limit=50`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setUploadStatus(`Success! Ingested ${data.comment_ids.length} comments from Twitter search`);
    } catch (error) {
      setUploadStatus('Error: ' + error.message);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert('Please select a file');
      return;
    }
    
    try {
      setUploadStatus('Uploading file...');
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/ingest/file', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const data = await response.json();
      setUploadStatus(`Success! Ingested ${data.comment_ids.length} comments from ${file.name}`);
    } catch (error) {
      setUploadStatus('Error: ' + error.message);
    }
  };

  return (
    <div className="tab-content">
      <h2>Smart Data Ingestion</h2>
      
      <div className="upload-section">
        <h3>YouTube Video</h3>
        <input 
          type="text" 
          placeholder="Paste YouTube URL" 
          value={youtubeUrl}
          onChange={(e) => setYoutubeUrl(e.target.value)}
        />
        <button onClick={handleYouTubeIngest}>Ingest Transcript</button>
      </div>
      
      <div className="upload-section">
        <h3>Web Article</h3>
        <input 
          type="text" 
          placeholder="Paste web article URL" 
          value={webUrl}
          onChange={(e) => setWebUrl(e.target.value)}
        />
        <button onClick={handleWebIngest}>Ingest Article</button>
      </div>
      
      <div className="upload-section">
        <h3>Twitter Data</h3>
        <input 
          type="text" 
          placeholder="Search query (e.g., '#policy')" 
          value={twitterQuery}
          onChange={(e) => setTwitterQuery(e.target.value)}
        />
        <button onClick={handleTwitterSearchIngest}>Search & Ingest</button>
        
        <input 
          type="text" 
          placeholder="Twitter username" 
          value={twitterUser}
          onChange={(e) => setTwitterUser(e.target.value)}
          style={{marginTop: '10px'}}
        />
        <button onClick={() => {
          if (!twitterUser) {
            alert('Please enter a Twitter username');
            return;
          }
          window.open(`http://localhost:8000/ingest/twitter/user?username=${encodeURIComponent(twitterUser)}&limit=50`, '_blank');
        }}>Ingest User Tweets</button>
      </div>
      
      <div className="upload-section">
        <h3>File Upload</h3>
        <input 
          type="file" 
          accept=".csv,.xlsx,.xls,.json" 
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button onClick={handleFileUpload}>Upload & Process</button>
      </div>
      
      {uploadStatus && (
        <div className="upload-status">
          <p>{uploadStatus}</p>
        </div>
      )}
      
      <div className="upload-instructions">
        <h3>Instructions</h3>
        <ul>
          <li>YouTube: Paste any YouTube video URL to extract the transcript</li>
          <li>Web: Paste any article URL to extract the content</li>
          <li>Twitter: Search for hashtags or topics, or ingest from a specific user</li>
          <li>Files: Upload CSV, Excel, or JSON files with comment data</li>
        </ul>
      </div>
    </div>
  );
}
```

#### Step 2: Update CSS for New Components

Update `frontend/src/App.css` to include styles for the new ingestion components:

```css
.upload-section {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.upload-section h3 {
  margin-top: 0;
  color: #333;
}

.upload-section input[type="text"] {
  width: 100%;
  padding: 8px;
  margin: 5px 0;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

.upload-section button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px 5px 5px 0;
}

.upload-section button:hover {
  background-color: #45a049;
}

.upload-status {
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
  background-color: #e7f3ff;
  border-left: 6px solid #2196F3;
}

.upload-instructions {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f8ff;
  border-radius: 5px;
}

.upload-instructions h3 {
  margin-top: 0;
}

.upload-instructions ul {
  padding-left: 20px;
}

.upload-instructions li {
  margin-bottom: 5px;
}
```

### 3. Testing and Verification

#### Step 1: Test Backend Endpoints
```bash
# Test YouTube ingestion
curl -X POST "http://localhost:8000/ingest/youtube?url=https://www.youtube.com/watch?v=example"

# Test web article ingestion
curl -X POST "http://localhost:8000/ingest/web?url=https://example.com/article"

# Test Twitter search ingestion
curl -X POST "http://localhost:8000/ingest/twitter/search?query=policy&limit=10"

# Test file ingestion
curl -X POST "http://localhost:8000/ingest/file" -F "file=@test.csv"
```

#### Step 2: Test Frontend Components
1. Start the backend server
2. Start the frontend development server
3. Navigate to the Upload tab
4. Test each ingestion method:
   - Paste a valid YouTube URL and click "Ingest Transcript"
   - Paste a valid web article URL and click "Ingest Article"
   - Enter a Twitter search query and click "Search & Ingest"
   - Upload a CSV/Excel/JSON file and click "Upload & Process"

### 4. Error Handling and Edge Cases

#### Common Issues to Handle:
1. Invalid URLs (YouTube, web, Twitter)
2. Videos without transcripts
3. Articles behind paywalls
4. Rate limiting from external services
5. Large files that take time to process
6. Network connectivity issues

#### Implementation:
Add proper error handling in all ingestion modules and display user-friendly error messages in the frontend.

### 5. Performance Optimization

#### For Large Datasets:
1. Implement batch processing for large files
2. Add progress indicators for long-running operations
3. Use background job processing for time-consuming tasks
4. Implement caching for frequently accessed data

### 6. Documentation Updates

Update the README.md to include information about the new ingestion capabilities:

```markdown
## Smart Data Ingestion

Sovereign's Edict now supports multiple data ingestion methods:

### YouTube Transcript Ingestion
Paste any YouTube video URL to automatically extract the transcript and process it as comments.

### Web Article Ingestion
Enter any web article URL to extract the content and analyze it.

### Twitter Data Ingestion
Search for hashtags or topics on Twitter, or ingest tweets from a specific user.

### File Upload
Upload CSV, Excel, or JSON files containing comment data for processing.

All ingestion methods are free and don't require any API keys.
```

## Next Steps

After implementing dynamic data ingestion:
1. Proceed to Phase 3: Automated Processing Pipeline
2. Update user documentation
3. Conduct testing with various data sources
4. Optimize performance for large datasets