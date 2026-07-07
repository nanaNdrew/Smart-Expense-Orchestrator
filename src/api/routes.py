import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.models import Receipt, TaskStatus
from src.schemas.receipt import TaskResponse, ReceiptResponse
from src.worker.tasks import process_receipt_task
from sqlalchemy import select

router = APIRouter()

UPLOAD_DIR = "/app/uploads"

@router.post("/receipts/upload", response_model=TaskResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename not provided")
        
    task_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    safe_filename = f"{task_id}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Ensure directory exists (useful for local testing outside docker)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Create DB record
    new_receipt = Receipt(
        task_id=task_id,
        status=TaskStatus.PENDING,
        filename=file.filename
    )
    db.add(new_receipt)
    await db.commit()
    
    # Enqueue background task
    process_receipt_task.delay(task_id, file_path)
    
    return TaskResponse(
        task_id=task_id,
        status="PENDING",
        message="Receipt uploaded and queued for processing"
    )

@router.get("/receipts/{task_id}", response_model=ReceiptResponse)
async def get_receipt(task_id: str, db: AsyncSession = Depends(get_db)):
    # Need joinedload to eagerly load line items
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Receipt).options(selectinload(Receipt.line_items)).where(Receipt.task_id == task_id)
    )
    receipt = result.scalar_one_or_none()
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
        
    return receipt
