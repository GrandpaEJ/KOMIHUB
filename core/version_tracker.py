"""Version tracking and update management for KOMIHUB"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

import aiohttp
import config
from core import logger


class VersionTracker:
    """Manages version checking and updates"""
    
    def __init__(self):
        self.version_file = Path("data/version.json")
        self.last_check = None
        self.current_versions = self._load_local_versions()
        
    def _load_local_versions(self) -> Dict:
        """Load current local versions"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load version file: {e}")
        
        # Default version info
        return {
            "v": "0.0.1",
            "tool": "0.0.1", 
            "komi": "0.0.1",
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_local_versions(self, versions: Dict) -> None:
        """Save versions to local file"""
        try:
            os.makedirs(self.version_file.parent, exist_ok=True)
            with open(self.version_file, 'w') as f:
                json.dump(versions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save version file: {e}")
    
    async def fetch_remote_versions(self) -> Optional[Dict]:
        """Fetch version info from remote API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.VERSION_URL) as response:
                    if response.status == 200:
                        data = await response.text()
                        # Handle the demo response format
                        if data.strip().startswith("#"):
                            # Demo response, return current versions
                            return self.current_versions
                        
                        versions = json.loads(data)
                        versions["last_check"] = datetime.now().isoformat()
                        return versions
        except Exception as e:
            logger.error(f"Failed to fetch remote versions: {e}")
        return None
    
    async def check_for_updates(self) -> Tuple[bool, str]:
        """Check if updates are available"""
        remote_versions = await self.fetch_remote_versions()
        if not remote_versions:
            return False, "Failed to check for updates"
        
        # Compare versions
        updates_available = []
        
        for component in ["v", "tool", "komi"]:
            remote_version = remote_versions.get(component, "0.0.1")
            local_version = self.current_versions.get(component, "0.0.1")
            
            if self._compare_versions(remote_version, local_version) > 0:
                updates_available.append(f"{component}: {local_version} → {remote_version}")
        
        if updates_available:
            self.last_check = datetime.now()
            return True, "\n".join(updates_available)
        
        return False, "All components are up to date"
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except:
            return 0  # If comparison fails, assume equal
    
    async def perform_update(self) -> Tuple[bool, str]:
        """Perform automatic update"""
        if not config.AUTO_UPDATE:
            return False, "Auto-update is disabled"
        
        try:
            logger.info("Starting auto-update process...")
            
            # Check if we're in a git repository
            if not self._is_git_repo():
                return False, "Not a git repository"
            
            # Get current branch
            current_branch = self._get_current_branch()
            
            # Fetch latest changes
            fetch_success = await self._git_fetch()
            if not fetch_success:
                return False, "Failed to fetch latest changes"
            
            # Get latest commit info
            latest_commit = self._get_latest_commit()
            
            # Check if we need to update
            if await self._is_up_to_date():
                return False, "Already up to date"
            
            # Perform the update
            update_success = await self._git_pull()
            if not update_success:
                return False, "Failed to pull latest changes"
            
            # Update local version info
            self.current_versions = self._load_local_versions()
            self._save_local_versions(self.current_versions)
            
            logger.info(f"Successfully updated to latest commit: {latest_commit}")
            return True, f"Updated to: {latest_commit}"
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return False, f"Update failed: {str(e)}"
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         check=True, capture_output=True)
            return True
        except:
            return False
    
    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "main"
    
    def _get_latest_commit(self) -> str:
        """Get latest commit hash and message"""
        try:
            result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h %s'], 
                                  check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "Unknown"
    
    async def _git_fetch(self) -> bool:
        """Perform git fetch"""
        try:
            process = await asyncio.create_subprocess_exec(
                'git', 'fetch', 'origin',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except:
            return False
    
    async def _git_pull(self) -> bool:
        """Perform git pull"""
        try:
            process = await asyncio.create_subprocess_exec(
                'git', 'pull', 'origin', 'main',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except:
            return False
    
    async def _is_up_to_date(self) -> bool:
        """Check if local repo is up to date with remote"""
        try:
            # Get local commit
            local_result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                        check=True, capture_output=True, text=True)
            local_commit = local_result.stdout.strip()
            
            # Get remote commit
            remote_result = subprocess.run(['git', 'rev-parse', 'origin/main'], 
                                         check=True, capture_output=True, text=True)
            remote_commit = remote_result.stdout.strip()
            
            return local_commit == remote_commit
        except:
            return True  # If check fails, assume up to date
    
    def should_check_for_updates(self) -> bool:
        """Check if it's time to check for updates"""
        if not config.AUTO_UPDATE:
            return False
        
        if not self.last_check:
            return True
        
        return datetime.now() - self.last_check >= timedelta(seconds=config.UPDATE_CHECK_INTERVAL)


# Global instance
version_tracker = VersionTracker()