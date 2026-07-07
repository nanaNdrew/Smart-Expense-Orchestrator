import pytest
from httpx import AsyncClient
from src.db.models import Receipt, TaskStatus
from sqlalchemy import select

@pytest.mark.asyncio
async def test_upload_receipt_success(async_client: AsyncClient, db_session, mocker):
    # Mock the Celery task delay so it doesn't actually try to connect to Redis/Celery
    mock_task = mocker.patch("src.api.routes.process_receipt_task.delay")
    
    # Create a dummy image file in memory
    files = {'file': ('test_receipt.jpg', b'dummy_image_data', 'image/jpeg')}
    
    response = await async_client.post("/api/v1/receipts/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "PENDING"
    
    task_id = data["task_id"]
    
    # Verify the Celery task was called
    mock_task.assert_called_once()
    args = mock_task.call_args[0]
    assert args[0] == task_id
    
    # Verify DB record was created
    result = await db_session.execute(select(Receipt).where(Receipt.task_id == task_id))
    receipt = result.scalar_one_or_none()
    
    assert receipt is not None
    assert receipt.filename == "test_receipt.jpg"
    assert receipt.status == TaskStatus.PENDING
