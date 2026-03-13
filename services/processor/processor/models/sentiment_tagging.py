"""
Content Emotional Tagging Engine

Extracts emotion from content using multi-modal analysis.
Classifies into 9 emotion categories with confidence scores.

Epic: #72 - AI Sentiment-Aware Feed Routing
Task: #78 - Content Emotional Tagging Engine
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Emotion(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ANGRY = "angry"
    SAD = "sad"
    HAPPY = "happy"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"


@dataclass
class EmotionScore:
    emotion: Emotion
    score: float
    
    def to_dict(self) -> Dict:
        return {"emotion": self.emotion.value, "score": self.score}


@dataclass 
class ContentEmotionProfile:
    content_id: str
    primary_emotion: Emotion
    emotion_scores: List[EmotionScore]
    overall_sentiment: str
    sentiment_confidence: float
    mixed_emotions: bool
    dominant_intensity: float
    
    def to_dict(self) -> Dict:
        return {
            "content_id": self.content_id,
            "primary_emotion": self.primary_emotion.value,
            "emotion_scores": [e.to_dict() for e in self.emotion_scores],
            "overall_sentiment": self.overall_sentiment,
            "sentiment_confidence": self.sentiment_confidence,
            "mixed_emotions": self.mixed_emotions,
            "dominant_intensity": self.dominant_intensity,
        }


class ContentEmotionalTagger:
    """
    Multi-modal emotion extraction from content.
    Analyzes text, images, and video frames.
    """
    
    EMOTION_TO_SENTIMENT = {
        Emotion.POSITIVE: "positive",
        Emotion.HAPPY: "positive",
        Emotion.SURPRISED: "positive",
        Emotion.NEGATIVE: "negative",
        Emotion.ANGRY: "negative",
        Emotion.SAD: "negative",
        Emotion.FEARFUL: "negative",
        Emotion.DISGUSTED: "negative",
        Emotion.NEUTRAL: "neutral",
    }
    
    def __init__(
        self,
        text_weight: float = 0.4,
        image_weight: float = 0.4,
        video_weight: float = 0.2,
        confidence_threshold: float = 0.3,
    ):
        self.text_weight = text_weight
        self.image_weight = image_weight
        self.video_weight = video_weight
        self.confidence_threshold = confidence_threshold
        
    def analyze_content(
        self,
        content_id: str,
        text: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        video_url: Optional[str] = None,
        frame_samples: int = 5,
    ) -> ContentEmotionProfile:
        """
        Analyze content and extract emotion profile.
        """
        text_emotions = self._analyze_text(text) if text else {}
        image_emotions = self._analyze_images(image_urls) if image_urls else {}
        video_emotions = self._analyze_video(video_url, frame_samples) if video_url else {}
        
        fused_emotions = self._fuse_emotions(
            text_emotions, image_emotions, video_emotions
        )
        
        emotion_scores = [
            EmotionScore(emotion=emotion, score=score)
            for emotion, score in fused_emotions.items()
            if score >= self.confidence_threshold
        ]
        
        emotion_scores.sort(key=lambda x: x.score, reverse=True)
        
        if not emotion_scores:
            primary_emotion = Emotion.NEUTRAL
            overall_sentiment = "neutral"
            sentiment_confidence = 1.0
            mixed_emotions = False
            dominant_intensity = 0.5
        else:
            primary_emotion