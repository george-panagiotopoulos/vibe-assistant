import re
import base64
from github import Github
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub repositories"""
    
    def __init__(self):
        self.github = None
        self.token = None
    
    def set_token(self, token):
        """Set GitHub authentication token"""
        if token and token != self.token:
            self.token = token
            self.github = Github(token)
        elif not token and not self.token:
            # Use public access (limited functionality)
            self.github = Github()
    
    def parse_repo_url(self, repo_url):
        """Parse GitHub repository URL to extract owner and repo name"""
        try:
            # Handle various GitHub URL formats
            if repo_url.startswith('https://github.com/'):
                path = urlparse(repo_url).path.strip('/')
                if path.endswith('.git'):
                    path = path[:-4]
                parts = path.split('/')
                if len(parts) >= 2:
                    return parts[0], parts[1]
            elif '/' in repo_url and not repo_url.startswith('http'):
                # Handle owner/repo format
                parts = repo_url.split('/')
                if len(parts) >= 2:
                    return parts[0], parts[1]
            
            raise ValueError("Invalid repository URL format")
        except Exception as e:
            logger.error(f"Error parsing repository URL: {str(e)}")
            raise ValueError(f"Invalid repository URL: {repo_url}")
    
    def get_repository_files(self, repo_url, branch='main'):
        """Get file tree structure for a repository"""
        try:
            owner, repo_name = self.parse_repo_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            try:
                contents = repo.get_contents("", ref=branch)
            except:
                # Try 'master' branch if 'main' doesn't exist
                contents = repo.get_contents("", ref='master')
                branch = 'master'
            
            file_tree = self._build_file_tree(repo, contents, branch)
            return {
                "tree": file_tree,
                "repository": {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "default_branch": branch,
                    "languages": list(repo.get_languages().keys())
                }
            }
        except Exception as e:
            logger.error(f"Error getting repository files: {str(e)}")
            raise Exception(f"Failed to access repository: {str(e)}")
    
    def _build_file_tree(self, repo, contents, branch, path=""):
        """Recursively build file tree structure"""
        tree = []
        
        for content in contents:
            node = {
                "name": content.name,
                "path": content.path,
                "type": content.type,
                "size": content.size if hasattr(content, 'size') else None,
                "sha": content.sha
            }
            
            if content.type == "dir":
                try:
                    # Get directory contents
                    dir_contents = repo.get_contents(content.path, ref=branch)
                    node["children"] = self._build_file_tree(repo, dir_contents, branch, content.path)
                    node["isExpanded"] = False
                except Exception as e:
                    logger.warning(f"Could not access directory {content.path}: {str(e)}")
                    node["children"] = []
                    node["error"] = "Access denied or empty directory"
            
            tree.append(node)
        
        # Sort: directories first, then files, both alphabetically
        tree.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
        return tree
    
    def get_file_content(self, repo_url, file_path, branch=None):
        """Get content of a specific file"""
        try:
            owner, repo_name = self.parse_repo_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            if not branch:
                branch = repo.default_branch
            
            file_content = repo.get_contents(file_path, ref=branch)
            
            if file_content.encoding == 'base64':
                content = base64.b64decode(file_content.content).decode('utf-8')
            else:
                content = file_content.content
            
            return {
                "content": content,
                "encoding": file_content.encoding,
                "size": file_content.size,
                "sha": file_content.sha,
                "path": file_content.path,
                "name": file_content.name
            }
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            raise Exception(f"Failed to get file content: {str(e)}")
    
    def search_files(self, repo_url, query, file_extensions=None):
        """Search for files in repository based on name or content"""
        try:
            owner, repo_name = self.parse_repo_url(repo_url)
            
            # Build search query
            search_query = f"repo:{owner}/{repo_name} {query}"
            if file_extensions:
                for ext in file_extensions:
                    search_query += f" extension:{ext}"
            
            # Search using GitHub API
            result = self.github.search_code(search_query)
            
            files = []
            for item in result:
                files.append({
                    "name": item.name,
                    "path": item.path,
                    "sha": item.sha,
                    "repository": item.repository.full_name,
                    "html_url": item.html_url
                })
            
            return files
        except Exception as e:
            logger.error(f"Error searching files: {str(e)}")
            raise Exception(f"Failed to search files: {str(e)}")
    
    def get_repository_info(self, repo_url):
        """Get basic repository information"""
        try:
            owner, repo_name = self.parse_repo_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "default_branch": repo.default_branch,
                "languages": repo.get_languages(),
                "topics": repo.get_topics(),
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "size": repo.size,
                "stargazers_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "open_issues_count": repo.open_issues_count,
                "license": repo.license.name if repo.license else None,
                "private": repo.private
            }
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            raise Exception(f"Failed to get repository info: {str(e)}") 