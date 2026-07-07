import base64
import time
from typing import Tuple
from openai import AsyncOpenAI
from src.core.config import settings
from src.core.logger import setup_logger
from src.schemas.receipt import ExtractedReceiptData

logger = setup_logger("llm_service")

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def extract_receipt_data(image_path: str) -> Tuple[ExtractedReceiptData, dict]:
    """
    Calls OpenAI GPT-4o to extract structured data from a receipt image.
    Returns the parsed Pydantic model and a dictionary with telemetry data.
    """
    start_time = time.time()
    
    try:
        base64_image = encode_image_to_base64(image_path)
    except Exception as e:
        logger.error(f"Failed to encode image at {image_path}: {str(e)}")
        raise

    prompt = (
        "You are an expert data entry assistant. Please extract the following information "
        "from the provided receipt image. Pay close attention to line items, taxes, "
        "and the total amount. If a field is not visible, leave it null/empty."
    )

    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format=ExtractedReceiptData,
        )
        
        execution_time = time.time() - start_time
        
        message = response.choices[0].message
        if message.parsed:
            extracted_data = message.parsed
        else:
            raise ValueError("Model refused or failed to output structured data.")
        
        usage = response.usage
        telemetry = {
            "execution_time_seconds": round(execution_time, 2),
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0
        }
        
        logger.info(
            "OpenAI API call successful",
            extra={
                "extra_info": {
                    "latency": execution_time,
                    "tokens": telemetry
                }
            }
        )
        
        return extracted_data, telemetry
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            f"OpenAI API call failed: {str(e)}", 
            extra={
                "extra_info": {
                    "latency": execution_time
                }
            },
            exc_info=True
        )
        raise
