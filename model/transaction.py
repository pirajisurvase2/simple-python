from pydantic import BaseModel
from typing import Literal,Optional
from datetime import date

class TransactionModel(BaseModel):
    borrower_id: str
    principal_amount: float
    interest_type: Literal["percentage", "flat"]
    interest_value: float
    frequency: Optional[Literal["daily", "monthly", "yearly"]] = None
    transaction_date: date
    note: Optional[str] = ""
