# models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    text_length = Column(Integer, nullable=False)
    num_chunks = Column(Integer, nullable=False)
    chunk_strategy = Column(String(50), nullable=False)
    chunk_size = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    document_metadata = Column(JSON)  # Store additional metadata if needed

class InterviewBooking(Base):
    __tablename__ = "interview_bookings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    date = Column(String(50), nullable=False)  # Store as string for simplicity
    time = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled