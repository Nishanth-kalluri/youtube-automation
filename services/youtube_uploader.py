# services/youtube_uploader.py
import os
import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from config import settings
from utils.logger import Logger

class YouTubeUploader:
    def __init__(self):
        self.logger = Logger(__name__)
        self.client_secrets_file = settings.YOUTUBE_CLIENT_SECRETS_PATH
        self.token_pickle_file = settings.YOUTUBE_TOKEN_PICKLE_PATH
    
    def get_credentials(self):
        """Get OAuth credentials for YouTube API"""
        credentials = None
        
        # Check if we have stored credentials
        if os.path.exists(self.token_pickle_file):
            self.logger.info(f"Loading credentials from {self.token_pickle_file}")
            with open(self.token_pickle_file, 'rb') as token:
                credentials = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                self.logger.info("Refreshing access token...")
                credentials.refresh(Request())
            else:
                self.logger.info("Getting new credentials...")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, ["https://www.googleapis.com/auth/youtube.upload"]
                )
                credentials = flow.run_local_server(port=8080)
            
            # Save credentials for next run
            self.logger.info(f"Saving credentials to {self.token_pickle_file}")
            with open(self.token_pickle_file, 'wb') as token:
                pickle.dump(credentials, token)
        
        return credentials
    
    def upload_video(self, video_path, title, description, tags=None):
        """
        Upload video to YouTube
        
        Args:
            video_path (str): Path to the video file
            title (str): Video title
            description (str): Video description
            tags (list, optional): List of tags
            
        Returns:
            dict: Upload response containing video ID and URL
        """
        self.logger.info(f"Uploading video: {title}")
        
        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            return {"error": "Video file not found"}
        
        try:
            # Get credentials and build service
            credentials = self.get_credentials()
            youtube = build("youtube", "v3", credentials=credentials)
            
            # Set tags if provided
            if tags is None:
                tags = ["auto-generated", "news"]
            
            # Define video metadata
            request_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags
                },
                "status": {
                    "privacyStatus": "private"  # Default to private
                }
            }
            
            # Create media file upload object
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            # Execute upload
            self.logger.info("Starting video upload to YouTube...")
            upload_request = youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=media
            )
            
            response = upload_request.execute()
            video_id = response['id']
            video_url = f"https://www.youtube.com/shorts/{video_id}"
            
            self.logger.info(f"Upload successful! Video ID: {video_id}, video URL:{video_url}")
            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url
            }
            
        except HttpError as e:
            self.logger.error(f"YouTube HTTP error: {e.resp.status} {e.content}")
            return {"error": f"YouTube HTTP error: {e.resp.status}"}
        except Exception as e:
            self.logger.error(f"Error uploading video: {e}")
            return {"error": str(e)}