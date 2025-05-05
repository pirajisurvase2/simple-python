from fastapi import APIRouter, Depends, status
from model.borrower import BorrowerModel
from typing import Optional
from services.borrower import (
    add_or_edit_borrower_service,
    delete_borrower_service,
    get_borrowers_service,
)
from services.auth import get_current_user
from utils.comman import custom_response


router = APIRouter(tags=["Barrower"])

@router.post("/")
async def add_borrower(
    borrower: BorrowerModel,
    borrower_id: str = None,
    current_user: dict = Depends(get_current_user),
):
    try:
        response = await add_or_edit_borrower_service(
            borrower, 
            borrower_id, 
            current_user["_id"]  # Pass lender_id from token
        )
        return response
    except ValueError as e:
        return custom_response(
            status.HTTP_401_UNAUTHORIZED,
            str(e)
        )
    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while adding borrower: {str(e)}"
        )

@router.get("/")
async def list_borrowers(
    search : Optional[str]=None,
    page: int = 1,  # Pagination: page number
    limit: int = 8,  # Pagination: number of items per page
    current_user: dict = Depends(get_current_user),  # Extracts lender_id from token
):
    try:
        response = await get_borrowers_service(
            search,
            current_user["_id"],  # Pass lender_id from token
            page,  # Pass page number
            limit  # Pass limit for number of borrowers per page
        )
        return response
    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while listing borrowers: {str(e)}"
        )

@router.delete("/{borrower_id}")
async def delete_borrower(
    borrower_id: str,
    current_user: dict = Depends(get_current_user),  # Extracts lender_id from token
):
    try:
        response = await delete_borrower_service(
            borrower_id,
            current_user["_id"]  # Pass lender_id from token
        )
        return response
    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error while deleting borrower: {str(e)}"
        )