from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from src.db.database import Base
import datetime
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    
    # Original file information
    filename = Column(String, nullable=True)
    
    # Extracted data
    merchant_name = Column(String, nullable=True)
    date = Column(String, nullable=True) # Stored as string to handle various formats from LLM or could use Date/DateTime if pre-parsed strictly
    total_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Error details if failed
    error_message = Column(String, nullable=True)

    # Relationships
    line_items = relationship("LineItem", back_populates="receipt", cascade="all, delete-orphan")

class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)

    # Relationships
    receipt = relationship("Receipt", back_populates="line_items")
