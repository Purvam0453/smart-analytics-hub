from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from datetime import datetime
from database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=0)
    username = Column(String, nullable=True, default="Guest")
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    predicted_role = Column(String, nullable=True)
    resume_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    skills = Column(Text, nullable=True)
    role_probabilities = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)