import asyncio
from src.worker.celery_app import celery_app
from src.core.logger import setup_logger
from src.db.database import AsyncSessionLocal
from src.db.models import Receipt, LineItem, TaskStatus
from src.services.llm_service import extract_receipt_data
from sqlalchemy import select

logger = setup_logger("celery_tasks")

async def process_receipt_async(task_id: str, file_path: str):
    logger.info(f"Starting processing for task_id: {task_id}")
    
    async with AsyncSessionLocal() as session:
        # Fetch the receipt record
        result = await session.execute(select(Receipt).where(Receipt.task_id == task_id))
        receipt = result.scalar_one_or_none()
        
        if not receipt:
            logger.error(f"Receipt record not found for task_id: {task_id}")
            return
            
        try:
            receipt.status = TaskStatus.PROCESSING
            await session.commit()
            
            # Extract data using OpenAI
            extracted_data, telemetry = await extract_receipt_data(file_path)
            
            # Update receipt record
            receipt.merchant_name = extracted_data.merchant_name
            receipt.date = extracted_data.date
            receipt.total_amount = extracted_data.total_amount
            receipt.tax_amount = extracted_data.tax_amount
            receipt.currency = extracted_data.currency
            
            # Add line items
            for item in extracted_data.line_items:
                line_item = LineItem(
                    receipt_id=receipt.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                session.add(line_item)
                
            receipt.status = TaskStatus.COMPLETED
            await session.commit()
            logger.info(f"Successfully processed task_id: {task_id}. Telemetry: {telemetry}")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
            receipt.status = TaskStatus.FAILED
            receipt.error_message = str(e)
            await session.commit()

@celery_app.task(bind=True, name="process_receipt_task")
def process_receipt_task(self, task_id: str, file_path: str):
    """
    Synchronous Celery task wrapper that runs the async processing function.
    """
    asyncio.run(process_receipt_async(task_id, file_path))
    return {"task_id": task_id, "status": "processed"}
