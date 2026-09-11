import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Text, DateTime

from .db import Base


class ModerationLog(Base):
    __tablename__ = "moderation_log"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    label = Column(String(20), nullable=False)
    confidence_safe = Column(Float, default=0.0)
    confidence_offensive = Column(Float, default=0.0)
    confidence_hate = Column(Float, default=0.0)
    explanation = Column(Text)  # stored as a JSON string
    source = Column(String(20), default="web")  # web / batch
    created_at = Column(DateTime, default=datetime.utcnow)
