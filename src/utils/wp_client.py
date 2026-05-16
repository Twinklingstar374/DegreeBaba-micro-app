import requests
import logging
from typing import Dict, Any, Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)

class WPClient:
    """
    WordPress client to check for existing posts by title and create/update posts.
    """

    def __init__(self, wp_url: str, wp_user: str, wp_password: str):
        self.wp_url = wp_url.rstrip('/')
        self.auth = (wp_user, wp_password)
        self.headers = {"Content-Type": "application/json"}

    def _get_posts(self, search_title: str, post_type: str = "pages") -> Optional[Dict]:
        """
        Search for a post by title.
        Returns the first matching post dictionary, or None if no match is found.
        """
        url = f"{self.wp_url}/wp-json/wp/v2/{post_type}"
        params = {"search": search_title, "_fields": "id,title"}
        
        try:
            response = requests.get(url, params=params, auth=self.auth, headers=self.headers)
            response.raise_for_status()
            posts = response.json()
            
            # WP search is broad, verify exact match if possible, or assume first result is best
            for post in posts:
                if search_title.lower() in post.get("title", {}).get("rendered", "").lower():
                    return post
            return None
        except Exception as e:
            logger.error(f"Failed to fetch posts from WordPress: {e}")
            return None

    def create_or_update_post(self, title: str, payload: Dict[str, Any], page_type: str) -> Dict[str, Any]:
        """
        Checks if a post exists by title. 
        If it exists, updates it. If not, creates a new draft.
        Prevents duplicates.
        """
        post_type = "pages"
        existing_post = self._get_posts(title, post_type=post_type)
        
        # Structure the payload for ACF (assuming ACF to REST API is enabled)
        wp_payload = {
            "title": title,
            "status": "draft",
            "acf": payload
        }
        
        if existing_post:
            post_id = existing_post["id"]
            logger.info(f"Post '{title}' exists (ID: {post_id}). Updating...")
            url = f"{self.wp_url}/wp-json/wp/v2/{post_type}/{post_id}"
            try:
                response = requests.post(url, json=wp_payload, auth=self.auth, headers=self.headers)
                response.raise_for_status()
                return {"status": "updated", "post_id": post_id, "url": url}
            except Exception as e:
                logger.error(f"Failed to update post: {e}")
                return {"status": "error", "message": str(e)}
        else:
            logger.info(f"Post '{title}' not found. Creating new draft...")
            url = f"{self.wp_url}/wp-json/wp/v2/{post_type}"
            try:
                response = requests.post(url, json=wp_payload, auth=self.auth, headers=self.headers)
                response.raise_for_status()
                created_post = response.json()
                return {"status": "created", "post_id": created_post.get("id"), "url": url}
            except Exception as e:
                logger.error(f"Failed to create post: {e}")
                return {"status": "error", "message": str(e)}
