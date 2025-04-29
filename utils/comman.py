from fastapi.responses import JSONResponse
from typing import Any, Optional
from datetime import datetime,date, time
from fastapi.exceptions import RequestValidationError
from bson import ObjectId
from datetime import datetime
import math



def custom_response(status: int = 200, message: str = "", rest: Optional[Any] = None):
    collection ={
            "status": status,
            "message": message
    }
    if rest:
        collection.update(rest)
    return JSONResponse(
        status_code=status,
        content=collection
    )

def custom_pagination_response(page: int, limit: int, total_count: int, docs: list):
    total_pages = math.ceil(total_count / limit)  # Calculate total pages
    return {
            "docs": docs,
            "page": page,
            "pages": total_pages,
            "limit": limit
    }



def convert_dates(val):
    if isinstance(val, date) and not isinstance(val, datetime):
        return datetime.combine(val, time.min)  
    return val 

async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    
    for error in exc.errors():
        field = error["loc"][-1]  
        msg = error["msg"]  
        errors.append({
            "field": field,
            "message": msg
        })

    return custom_response(400, "Validation error", {
        "errors" : errors
    })



def serialize_value(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value

def serialize_mongo_document(doc: dict) -> dict:
    return {key: serialize_value(value) for key, value in doc.items()}

def serialize_mongo_documents(docs: list[dict]) -> list[dict]:
    return [serialize_mongo_document(doc) for doc in docs]


def calculate_interest(principal, interest_type, value):
    if interest_type == "percentage":
        interest_amount = principal * value / 100
    else:
        interest_amount = value
    return interest_amount