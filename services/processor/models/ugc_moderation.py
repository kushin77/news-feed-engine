"""
Placeholder for UGC moderation model.

This will classify user-submitted content (text/video/audio) for policy
compliance before ingestion into the processing pipeline.  Milestone 89
requires only the design stub.
"""

from typing import Any


class UGCModerationModel:
    def __init__(self):
        self.labels = ['safe', 'nsfw', 'spam', 'abuse']

    def predict(self, content: Any) -> str:
        # stub: always safe
        return 'safe'

    @staticmethod
    def load(path: str):
        # stub loader
        return UGCModerationModel()
