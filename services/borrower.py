from bson import ObjectId
from fastapi import status
from model.borrower import BorrowerModel
from database import borrower_collection
from utils.comman import custom_response, convert_dates,custom_pagination_response
from datetime import datetime

async def add_or_edit_borrower_service(
    borrower: BorrowerModel,
    borrower_id: str = None,
    lender_id: str = None  # Comes from token (current_user["_id"])
):
    try:
        borrower_data = borrower.dict()
        borrower_data["dob"] = convert_dates(borrower.dob)
        borrower_data["lender_id"] = lender_id  # Add lender_id to stored data

        if borrower_id:
            # Ensure borrower exists and belongs to the lender
            existing_borrower = await borrower_collection.find_one(
                {"_id": ObjectId(borrower_id), "lender_id": lender_id}
            )
            if not existing_borrower:
                return custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Borrower not found or access denied"
                )

            # Update borrower
            result = await borrower_collection.update_one(
                {"_id": ObjectId(borrower_id)},
                {"$set": borrower_data}
            )
            if result.modified_count == 0:
                return custom_response(
                    status.HTTP_400_BAD_REQUEST,
                    "No changes made to borrower"
                )
            return custom_response(
                status.HTTP_200_OK,
                "Borrower updated successfully"
            )

        # Insert new borrower (with lender_id)
        await borrower_collection.insert_one(borrower_data)
        return custom_response(
            status.HTTP_200_OK,
            "Borrower added successfully"
        )

    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Service error: {str(e)}"
        )

async def get_borrowers_service(
    first_name: str,
    last_name: str,
    email: str,
    lender_id: str,
    page: int = 1,
    limit: int = 8  # Default limit for pagination
):
    try:
        query = {"lender_id": lender_id}
        if first_name:
            query["first_name"] = {"$regex": first_name, "$options": "i"}
        if last_name:
            query["last_name"] = {"$regex": last_name, "$options": "i"}
        if email:
            query["email"] = {"$regex": email, "$options": "i"}

        # cursor = await borrower_collection.find(query).to_list(100)  # Fetch all results as a list
        skip_value = (page - 1) * limit
        
        # Fetch paginated results
        cursor = await borrower_collection.find(query).skip(skip_value).limit(limit).to_list(limit)

        # Get total count for pagination calculation
        total_count = await borrower_collection.count_documents(query)
        borrowers = []
        for borrower in cursor:
            borrower["_id"] = str(borrower["_id"])  # Convert ObjectId to string
            if "dob" in borrower and isinstance(borrower["dob"], datetime):
                borrower["dob"] = borrower["dob"].isoformat()
            borrower_info = {
                "_id" : borrower["_id"],
                "full_name": f"{borrower['first_name']} {borrower['last_name']}",
                "email": borrower["email"],
                "phone": borrower["phone"],
                "dob": borrower["dob"],
                "address": borrower["address"]
            }
            borrowers.append(borrower_info)
        pagination_response = custom_pagination_response(page, limit, total_count, borrowers)
        return custom_response(
            status.HTTP_200_OK,
            "Borrowers retrieved successfully",
            {"data": pagination_response}
        )
    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Service error: {str(e)}"
        )

async def delete_borrower_service(
    borrower_id: str,
    lender_id: str  # Comes from token (current_user["_id"])
):
    try:
        # Ensure borrower exists and belongs to the lender
        borrower = await borrower_collection.find_one(
            {"_id": ObjectId(borrower_id), "lender_id": lender_id}
        )
        if not borrower:
            return custom_response(
                status.HTTP_404_NOT_FOUND,
                "Borrower not found or access denied"
            )

        result = await borrower_collection.delete_one(
            {"_id": ObjectId(borrower_id)}
        )
        if result.deleted_count == 0:
            return custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Error deleting borrower"
            )
        return custom_response(
            status.HTTP_200_OK,
            "Borrower deleted successfully"
        )
    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Service error: {str(e)}"
        )