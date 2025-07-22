"""
Feedback Collector - Intelligent user feedback collection and analysis system

This module provides comprehensive feedback collection capabilities including
automated feedback gathering, sentiment analysis, and feedback categorization
to continuously improve the development framework.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """Types of feedback that can be collected"""
    TEMPLATE_QUALITY = "template_quality"
    WORKFLOW_EFFICIENCY = "workflow_efficiency"
    CODE_GENERATION = "code_generation"
    USER_EXPERIENCE = "user_experience"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"

class SentimentLevel(Enum):
    """Sentiment levels for feedback analysis"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

@dataclass
class FeedbackEntry:
    """Represents a single feedback entry"""
    feedback_id: str
    project_id: str
    user_id: str
    feedback_type: FeedbackType
    rating: int  # 1-5 scale
    title: str
    description: str
    context: Dict[str, Any]
    sentiment_score: float  # -1.0 to 1.0
    sentiment_level: SentimentLevel
    keywords: List[str]
    priority: str  # low, medium, high, critical
    created_at: str
    processed: bool = False
    response: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class FeedbackSummary:
    """Summary of feedback analysis"""
    total_feedback: int
    avg_rating: float
    sentiment_distribution: Dict[str, int]
    top_issues: List[Tuple[str, int]]
    improvement_suggestions: List[str]
    priority_items: List[str]
    trend_analysis: Dict[str, Any]

class FeedbackCollector:
    """
    Intelligent feedback collection and analysis system
    """
    
    def __init__(self, db_path: str = "feedback_data.db"):
        """Initialize the feedback collector"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Sentiment analysis keywords
        self.positive_keywords = {
            'excellent', 'amazing', 'great', 'good', 'helpful', 'useful', 'efficient',
            'fast', 'easy', 'intuitive', 'love', 'perfect', 'awesome', 'fantastic',
            'brilliant', 'outstanding', 'impressive', 'smooth', 'clean', 'elegant'
        }
        
        self.negative_keywords = {
            'terrible', 'awful', 'bad', 'poor', 'useless', 'slow', 'difficult',
            'confusing', 'broken', 'buggy', 'frustrating', 'annoying', 'horrible',
            'disappointing', 'complicated', 'messy', 'unclear', 'hard', 'hate'
        }
        
        # Issue categorization patterns
        self.issue_patterns = {
            'performance': ['slow', 'lag', 'timeout', 'performance', 'speed', 'memory'],
            'usability': ['confusing', 'difficult', 'hard to use', 'unclear', 'complex'],
            'bugs': ['error', 'crash', 'bug', 'broken', 'fail', 'exception'],
            'features': ['missing', 'need', 'want', 'request', 'add', 'include'],
            'documentation': ['docs', 'documentation', 'help', 'guide', 'tutorial'],
            'integration': ['compatibility', 'integration', 'connect', 'sync', 'import']
        }
        
        logger.info("Feedback collector initialized")
    
    def _init_database(self):
        """Initialize the feedback database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS feedback_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_id TEXT UNIQUE NOT NULL,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    context TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    sentiment_level TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    processed BOOLEAN DEFAULT 0,
                    response TEXT,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS feedback_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT NOT NULL,
                    analysis_data TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    preference_type TEXT NOT NULL,
                    preference_value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_feedback_project ON feedback_entries(project_id);
                CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback_entries(user_id);
                CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback_entries(feedback_type);
                CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback_entries(rating);
                CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback_entries(created_at);
            """)
    
    def collect_feedback(self, feedback: FeedbackEntry) -> bool:
        """Collect and store a feedback entry"""
        try:
            # Analyze sentiment if not provided
            if feedback.sentiment_score == 0.0:
                feedback.sentiment_score = self._analyze_sentiment(feedback.description)
                feedback.sentiment_level = self._get_sentiment_level(feedback.sentiment_score)
            
            # Extract keywords if not provided
            if not feedback.keywords:
                feedback.keywords = self._extract_keywords(feedback.description)
            
            # Determine priority if not provided
            if not hasattr(feedback, 'priority') or not feedback.priority:
                feedback.priority = self._determine_priority(feedback)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO feedback_entries 
                    (feedback_id, project_id, user_id, feedback_type, rating,
                     title, description, context, sentiment_score, sentiment_level,
                     keywords, priority, created_at, processed, response, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.feedback_id,
                    feedback.project_id,
                    feedback.user_id,
                    feedback.feedback_type.value,
                    feedback.rating,
                    feedback.title,
                    feedback.description,
                    json.dumps(feedback.context),
                    feedback.sentiment_score,
                    feedback.sentiment_level.value,
                    json.dumps(feedback.keywords),
                    feedback.priority,
                    feedback.created_at,
                    feedback.processed,
                    feedback.response,
                    json.dumps(feedback.metadata or {})
                ))
            
            logger.info(f"Collected feedback: {feedback.feedback_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
            return False
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of feedback text"""
        try:
            text_lower = text.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            positive_count = sum(1 for word in words if word in self.positive_keywords)
            negative_count = sum(1 for word in words if word in self.negative_keywords)
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return 0.0  # Neutral
            
            # Calculate sentiment score (-1.0 to 1.0)
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            
            # Adjust based on text length and context
            if len(words) > 50:  # Longer text, more reliable
                sentiment_score *= 1.2
            
            # Clamp to [-1.0, 1.0]
            return max(-1.0, min(1.0, sentiment_score))
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return 0.0
    
    def _get_sentiment_level(self, score: float) -> SentimentLevel:
        """Convert sentiment score to level"""
        if score >= 0.6:
            return SentimentLevel.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentLevel.POSITIVE
        elif score >= -0.2:
            return SentimentLevel.NEUTRAL
        elif score >= -0.6:
            return SentimentLevel.NEGATIVE
        else:
            return SentimentLevel.VERY_NEGATIVE
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from feedback text"""
        try:
            text_lower = text.lower()
            
            # Extract technical terms and important words
            keywords = []
            
            # Check for issue patterns
            for category, patterns in self.issue_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        keywords.append(f"issue:{category}")
            
            # Extract common technical terms
            tech_terms = re.findall(r'\b(?:api|ui|ux|performance|bug|feature|template|workflow|integration|documentation)\b', text_lower)
            keywords.extend(tech_terms)
            
            # Extract quoted terms (likely important)
            quoted_terms = re.findall(r'"([^"]*)"', text)
            keywords.extend([term.lower() for term in quoted_terms if len(term) > 2])
            
            # Remove duplicates and return
            return list(set(keywords))
            
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            return []
    
    def _determine_priority(self, feedback: FeedbackEntry) -> str:
        """Determine feedback priority based on content and context"""
        try:
            priority_score = 0
            
            # Rating-based priority
            if feedback.rating <= 2:
                priority_score += 3  # Low rating = higher priority
            elif feedback.rating >= 4:
                priority_score += 1  # High rating = lower priority
            
            # Sentiment-based priority
            if feedback.sentiment_score <= -0.5:
                priority_score += 2  # Very negative = higher priority
            
            # Keyword-based priority
            critical_keywords = ['crash', 'error', 'broken', 'fail', 'bug', 'security']
            high_keywords = ['slow', 'performance', 'usability', 'confusing']
            
            text_lower = feedback.description.lower()
            
            for keyword in critical_keywords:
                if keyword in text_lower:
                    priority_score += 3
            
            for keyword in high_keywords:
                if keyword in text_lower:
                    priority_score += 2
            
            # Feedback type priority
            if feedback.feedback_type == FeedbackType.BUG_REPORT:
                priority_score += 2
            elif feedback.feedback_type == FeedbackType.PERFORMANCE:
                priority_score += 2
            
            # Determine final priority
            if priority_score >= 6:
                return "critical"
            elif priority_score >= 4:
                return "high"
            elif priority_score >= 2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Failed to determine priority: {e}")
            return "medium"
    
    def analyze_feedback_trends(self, days: int = 30) -> FeedbackSummary:
        """Analyze feedback trends over specified period"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Get recent feedback
                cursor = conn.execute("""
                    SELECT rating, sentiment_level, keywords, description, feedback_type, priority
                    FROM feedback_entries 
                    WHERE created_at >= ?
                    ORDER BY created_at DESC
                """, (cutoff_date,))
                
                feedback_data = cursor.fetchall()
                
                if not feedback_data:
                    return FeedbackSummary(
                        total_feedback=0,
                        avg_rating=0.0,
                        sentiment_distribution={},
                        top_issues=[],
                        improvement_suggestions=[],
                        priority_items=[],
                        trend_analysis={}
                    )
                
                # Calculate metrics
                ratings = [row[0] for row in feedback_data]
                avg_rating = sum(ratings) / len(ratings)
                
                # Sentiment distribution
                sentiment_counts = Counter(row[1] for row in feedback_data)
                
                # Extract all keywords
                all_keywords = []
                for row in feedback_data:
                    keywords = json.loads(row[2]) if row[2] else []
                    all_keywords.extend(keywords)
                
                # Top issues
                keyword_counts = Counter(all_keywords)
                top_issues = keyword_counts.most_common(10)
                
                # Priority items
                priority_items = []
                for row in feedback_data:
                    if row[5] in ['critical', 'high']:  # priority column
                        priority_items.append(row[3][:100])  # First 100 chars of description
                
                # Generate improvement suggestions
                improvement_suggestions = self._generate_improvement_suggestions(feedback_data)
                
                # Trend analysis
                trend_analysis = self._analyze_trends(conn, days)
                
                return FeedbackSummary(
                    total_feedback=len(feedback_data),
                    avg_rating=avg_rating,
                    sentiment_distribution=dict(sentiment_counts),
                    top_issues=top_issues,
                    improvement_suggestions=improvement_suggestions,
                    priority_items=priority_items[:5],  # Top 5 priority items
                    trend_analysis=trend_analysis
                )
                
        except Exception as e:
            logger.error(f"Failed to analyze feedback trends: {e}")
            return FeedbackSummary(
                total_feedback=0,
                avg_rating=0.0,
                sentiment_distribution={},
                top_issues=[],
                improvement_suggestions=[],
                priority_items=[],
                trend_analysis={}
            )
    
    def _generate_improvement_suggestions(self, feedback_data: List[Tuple]) -> List[str]:
        """Generate improvement suggestions based on feedback analysis"""
        suggestions = []
        
        try:
            # Analyze common issues
            issue_categories = defaultdict(int)
            low_ratings = []
            
            for row in feedback_data:
                rating, sentiment, keywords_json, description, feedback_type, priority = row
                keywords = json.loads(keywords_json) if keywords_json else []
                
                if rating <= 2:
                    low_ratings.append(description)
                
                for keyword in keywords:
                    if keyword.startswith('issue:'):
                        category = keyword.split(':')[1]
                        issue_categories[category] += 1
            
            # Generate suggestions based on common issues
            for category, count in issue_categories.items():
                if count >= 3:  # Significant number of issues
                    if category == 'performance':
                        suggestions.append("Consider optimizing system performance and response times")
                    elif category == 'usability':
                        suggestions.append("Improve user interface design and user experience")
                    elif category == 'bugs':
                        suggestions.append("Increase testing coverage and bug detection processes")
                    elif category == 'features':
                        suggestions.append("Evaluate and prioritize requested feature additions")
                    elif category == 'documentation':
                        suggestions.append("Enhance documentation quality and coverage")
                    elif category == 'integration':
                        suggestions.append("Improve integration capabilities and compatibility")
            
            # Analyze low rating feedback for specific suggestions
            if len(low_ratings) >= 3:
                suggestions.append("Address critical user satisfaction issues identified in low-rated feedback")
            
            return suggestions[:5]  # Top 5 suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate improvement suggestions: {e}")
            return []
    
    def _analyze_trends(self, conn, days: int) -> Dict[str, Any]:
        """Analyze feedback trends over time"""
        try:
            # Get weekly data for trend analysis
            cursor = conn.execute("""
                SELECT 
                    DATE(created_at) as date,
                    AVG(rating) as avg_rating,
                    COUNT(*) as feedback_count,
                    AVG(sentiment_score) as avg_sentiment
                FROM feedback_entries 
                WHERE created_at >= ?
                GROUP BY DATE(created_at)
                ORDER BY date
            """, ((datetime.now() - timedelta(days=days)).isoformat(),))
            
            daily_data = cursor.fetchall()
            
            if len(daily_data) < 2:
                return {'status': 'insufficient_data'}
            
            # Calculate trends
            ratings = [row[1] for row in daily_data]
            counts = [row[2] for row in daily_data]
            sentiments = [row[3] for row in daily_data]
            
            # Simple trend calculation (positive/negative/stable)
            rating_trend = "stable"
            if len(ratings) >= 7:
                recent_avg = sum(ratings[-7:]) / 7
                older_avg = sum(ratings[:-7]) / (len(ratings) - 7)
                
                if recent_avg > older_avg * 1.1:
                    rating_trend = "improving"
                elif recent_avg < older_avg * 0.9:
                    rating_trend = "declining"
            
            return {
                'rating_trend': rating_trend,
                'avg_daily_feedback': sum(counts) / len(counts),
                'sentiment_trend': sum(sentiments) / len(sentiments),
                'data_points': len(daily_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {'status': 'error'}
    
    def get_feedback_by_project(self, project_id: str) -> List[FeedbackEntry]:
        """Get all feedback for a specific project"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM feedback_entries WHERE project_id = ?
                    ORDER BY created_at DESC
                """, (project_id,))
                
                feedback_list = []
                for row in cursor.fetchall():
                    feedback = FeedbackEntry(
                        feedback_id=row[1],
                        project_id=row[2],
                        user_id=row[3],
                        feedback_type=FeedbackType(row[4]),
                        rating=row[5],
                        title=row[6],
                        description=row[7],
                        context=json.loads(row[8]),
                        sentiment_score=row[9],
                        sentiment_level=SentimentLevel(row[10]),
                        keywords=json.loads(row[11]),
                        priority=row[12],
                        created_at=row[13],
                        processed=bool(row[14]),
                        response=row[15],
                        metadata=json.loads(row[16]) if row[16] else {}
                    )
                    feedback_list.append(feedback)
                
                return feedback_list
                
        except Exception as e:
            logger.error(f"Failed to get feedback for project {project_id}: {e}")
            return []
    
    def mark_feedback_processed(self, feedback_id: str, response: str = None) -> bool:
        """Mark feedback as processed with optional response"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE feedback_entries 
                    SET processed = 1, response = ?
                    WHERE feedback_id = ?
                """, (response, feedback_id))
                
            logger.info(f"Marked feedback {feedback_id} as processed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark feedback as processed: {e}")
            return False
    
    def export_feedback_report(self, output_path: str, days: int = 30) -> bool:
        """Export comprehensive feedback report"""
        try:
            # Get feedback summary
            summary = self.analyze_feedback_trends(days)
            
            # Get detailed feedback data
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM feedback_entries 
                    WHERE created_at >= ?
                    ORDER BY created_at DESC
                """, (cutoff_date,))
                
                columns = [desc[0] for desc in cursor.description]
                feedback_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Create comprehensive report
            report = {
                'report_generated': datetime.now().isoformat(),
                'period_days': days,
                'summary': asdict(summary),
                'detailed_feedback': feedback_data,
                'statistics': {
                    'total_users': len(set(item['user_id'] for item in feedback_data)),
                    'total_projects': len(set(item['project_id'] for item in feedback_data)),
                    'feedback_types': dict(Counter(item['feedback_type'] for item in feedback_data)),
                    'priority_distribution': dict(Counter(item['priority'] for item in feedback_data))
                }
            }
            
            # Write report
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Exported feedback report to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export feedback report: {e}")
            return False
    
    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary statistics for feedback collection"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Total feedback count
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM feedback_entries
                    WHERE created_at >= ?
                """, (cutoff_date,))
                total_feedback = cursor.fetchone()[0] or 0
                
                # Average rating
                cursor = conn.execute("""
                    SELECT AVG(rating) FROM feedback_entries
                    WHERE created_at >= ?
                """, (cutoff_date,))
                avg_rating = cursor.fetchone()[0] or 0.0
                
                # Sentiment distribution
                cursor = conn.execute("""
                    SELECT sentiment_level, COUNT(*) FROM feedback_entries
                    WHERE created_at >= ?
                    GROUP BY sentiment_level
                """, (cutoff_date,))
                sentiment_dist = dict(cursor.fetchall())
                
                return {
                    'total_feedback': total_feedback,
                    'avg_rating': avg_rating,
                    'sentiment_distribution': sentiment_dist,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            return {
                'total_feedback': 0,
                'avg_rating': 0.0,
                'sentiment_distribution': {},
                'period_days': days
            }


if __name__ == "__main__":
    # Example usage
    collector = FeedbackCollector()
    
    # Example feedback entry
    feedback = FeedbackEntry(
        feedback_id="feedback_001",
        project_id="test_project_001",
        user_id="user_123",
        feedback_type=FeedbackType.TEMPLATE_QUALITY,
        rating=4,
        title="Great template, minor issues",
        description="The React template is excellent and saves a lot of time. However, the build process is a bit slow and could be optimized.",
        context={"template_name": "react_typescript", "build_time": 45},
        sentiment_score=0.0,  # Will be calculated
        sentiment_level=SentimentLevel.NEUTRAL,  # Will be calculated
        keywords=[],  # Will be extracted
        priority="",  # Will be determined
        created_at=datetime.now().isoformat()
    )
    
    # Collect feedback and analyze
    collector.collect_feedback(feedback)
    summary = collector.analyze_feedback_trends(30)
    
    print("Feedback Collector Demo:")
    print(f"Summary: {asdict(summary)}")
