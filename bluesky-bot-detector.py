import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import re

@dataclass
class UserProfile:
    """Represents a user's profile and activity metadata"""
    user_id: str
    username: str
    creation_date: datetime
    posts: List[Dict] = field(default_factory=list)
    followers_count: int = 0
    following_count: int = 0
    bot_score: float = 0.0
    is_bot: bool = False

class BotDetector:
    def __init__(self, threshold: float = 0.7):
        """
        Initialize bot detection system with configurable threshold
        
        Args:
            threshold (float): Probability threshold for bot classification
        """
        self.threshold = threshold
        self.blocklist: List[str] = []
        self.detection_rules = {
            'post_frequency': self._check_post_frequency,
            'content_similarity': self._check_content_similarity,
            'network_interaction': self._check_network_interaction,
            'account_age': self._check_account_age
        }
    
    def _check_post_frequency(self, user: UserProfile) -> float:
        """
        Analyze posting frequency for bot-like behavior
        
        Args:
            user: User profile to analyze
        Returns:
            Bot likelihood score based on posting patterns
        """
        if not user.posts:
            return 0.0
        
        # Calculate posts per day since account creation
        days_active = max(1, (datetime.now() - user.creation_date).days)
        posts_per_day = len(user.posts) / days_active
        
        # Excessive posting suggests potential bot activity
        if posts_per_day > 20:
            return 0.8
        elif posts_per_day > 10:
            return 0.5
        return 0.1
    
    def _check_content_similarity(self, user: UserProfile) -> float:
        """
        Check for repetitive or machine-generated content
        
        Args:
            user: User profile to analyze
        Returns:
            Bot likelihood score based on content patterns
        """
        if len(user.posts) < 5:
            return 0.0
        
        # Extract text content
        contents = [post.get('text', '') for post in user.posts]
        
        # Check for high text similarity
        unique_contents = set(contents)
        similarity_score = 1 - (len(unique_contents) / len(contents))
        
        return min(similarity_score * 1.5, 0.9)
    
    def _check_network_interaction(self, user: UserProfile) -> float:
        """
        Analyze network interaction patterns
        
        Args:
            user: User profile to analyze
        Returns:
            Bot likelihood score based on follower/following ratios
        """
        # Suspicious network dynamics
        if user.followers_count == 0:
            return 0.7
        
        follow_ratio = user.following_count / max(user.followers_count, 1)
        
        if follow_ratio > 10:
            return 0.8
        elif follow_ratio > 5:
            return 0.5
        return 0.1
    
    def _check_account_age(self, user: UserProfile) -> float:
        """
        Assess account age and potential bot characteristics
        
        Args:
            user: User profile to analyze
        Returns:
            Bot likelihood score based on account creation date
        """
        account_age = (datetime.now() - user.creation_date).days
        
        if account_age < 30:
            return 0.6
        elif account_age < 90:
            return 0.3
        return 0.1
    
    def detect_bot(self, user: UserProfile) -> bool:
        """
        Comprehensive bot detection method
        
        Args:
            user: User profile to analyze
        Returns:
            Boolean indicating if user is likely a bot
        """
        # Calculate bot scores across different detection rules
        bot_scores = [
            rule(user) for rule in self.detection_rules.values()
        ]
        
        user.bot_score = np.mean(bot_scores)
        user.is_bot = user.bot_score >= self.threshold
        
        if user.is_bot:
            self.blocklist.append(user.user_id)
        
        return user.is_bot
    
    def export_blocklist(self, filename: str = 'blocklist.json'):
        """
        Export current blocklist to a JSON file
        
        Args:
            filename: Output file for blocklist
        """
        with open(filename, 'w') as f:
            json.dump(self.blocklist, f)
    
    def import_blocklist(self, filename: str = 'blocklist.json'):
        """
        Import blocklist from a JSON file
        
        Args:
            filename: Input file for blocklist
        """
        try:
            with open(filename, 'r') as f:
                self.blocklist = json.load(f)
        except FileNotFoundError:
            print(f"Blocklist file {filename} not found.")

def main():
    # Example usage
    detector = BotDetector(threshold=0.6)
    
    # Simulated user profiles for demonstration
    users = [
        UserProfile(
            user_id='user1', 
            username='realuser', 
            creation_date=datetime.now() - timedelta(days=365),
            followers_count=100,
            following_count=80,
            posts=[
                {'text': 'Hello world'},
                {'text': 'Nice day today'},
                {'text': 'Enjoying the weekend'}
            ]
        ),
        UserProfile(
            user_id='user2', 
            username='suspiciousbot', 
            creation_date=datetime.now() - timedelta(days=15),
            followers_count=5,
            following_count=200,
            posts=[
                {'text': 'Buy now!'} for _ in range(50)
            ]
        )
    ]
    
    # Detect bots
    for user in users:
        is_bot = detector.detect_bot(user)
        print(f"User {user.username}: Bot Score = {user.bot_score:.2f}, Is Bot = {is_bot}")
    
    # Export blocklist
    detector.export_blocklist()

if __name__ == "__main__":
    main()
