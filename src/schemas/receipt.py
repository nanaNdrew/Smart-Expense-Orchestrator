from pydantic import BaseModel, Field
from typing import List, Optional
from src.db.models import TaskStatus

class ExtractedLineItem(BaseModel):
    description: str = Field(..., description="Description of the purchased item")
    quantity: Optional[float] = Field(None, description="Quantity of the item purchased")
    unit_price: Optional[float] = Field(None, description="Unit price of the item")

class ExtractedReceiptData(BaseModel):
    merchant_name: Optional[str] = Field(None, description="Name of the merchant or store")
    date: Optional[str] = Field(None, description="Date of the receipt in YYYY-MM-DD format if possible")
    total_amount: Optional[float] = Field(None, description="Total amount paid")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    currency: Optional[str] = Field(None, description="Currency code (e.g. USD, EUR, GBP)")
    line_items: List[ExtractedLineItem] = Field(default_factory=list, description="List of items purchased")

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class LineItemResponse(BaseModel):
    id: int
    description: str
    quantity: Optional[float]
    unit_price: Optional[float]

    model_config = {"from_attributes": True}

class ReceiptResponse(BaseModel):
    id: int
    task_id: str
    status: TaskStatus
    filename: Optional[str]
    merchant_name: Optional[str]
    date: Optional[str]
    total_amount: Optional[float]
    tax_amount: Optional[float]
    currency: Optional[str]
    line_items: List[LineItemResponse]

    model_config = {"from_attributes": True}
