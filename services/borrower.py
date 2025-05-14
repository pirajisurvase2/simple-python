from bson import ObjectId
from fastapi import status
from model.borrower import BorrowerModel
from database import borrower_collection
from utils.comman import custom_response, convert_dates,custom_pagination_response
from pymongo import DESCENDING

async def add_or_edit_borrower_service(
    borrower: BorrowerModel,
    _id: str = None,
    lender_id: str = None  # Comes from token (current_user["_id"])
):
    try:
        borrower_data = borrower.dict()
        borrower_data["dob"] = convert_dates(borrower.dob)
        borrower_data["lender_id"] = lender_id  # Add lender_id to stored data

        if _id:
            # Ensure borrower exists and belongs to the lender
            existing_borrower = await borrower_collection.find_one(
                {"_id": ObjectId(_id), "lender_id": lender_id}
            )
            if not existing_borrower:
                return custom_response(
                    status.HTTP_404_NOT_FOUND,
                    "Borrower not found or access denied"
                )

            # Update borrower
            result = await borrower_collection.update_one(
                {"_id": ObjectId(_id)},
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
    search : str,
    lender_id: str,
    page: int = 1,
    limit: int = 8  # Default limit for pagination
):
    try:
        query = {"lender_id": lender_id}
        if search:
            query["$or"] = [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
            
        skip_value = (page - 1) * limit
        
        # Fetch paginated results
        cursor = await borrower_collection.find(query).sort("_id", DESCENDING).skip(skip_value).limit(limit).to_list(limit)

        # Get total count for pagination calculation
        total_count = await borrower_collection.count_documents(query)
        borrowers = []
        for borrower in cursor:
            borrower["_id"] = str(borrower["_id"]) 
            if "lender_id" in borrower:
                del borrower["lender_id"] 
            borrowers.append(borrower)
        pagination_response = custom_pagination_response(page, limit, total_count, cursor)
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
    
async def get_borrower_details_service(
    borrower_id: str,
    lender_id: str  # Comes from the current_user["_id"]
):
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(borrower_id):
            return custom_response(
                status.HTTP_400_BAD_REQUEST,
                "Invalid borrower ID format"
            )

        # Find borrower who belongs to the current lender
        borrower = await borrower_collection.find_one(
            {"_id": ObjectId(borrower_id), "lender_id": lender_id},
            {"_id": 1, "name": 1, "email": 1, "phone": 1, "address": 1, "created_at": 1}  # Return only necessary fields
        )

        if not borrower:
            return custom_response(
                status.HTTP_404_NOT_FOUND,
                "Borrower not found or access denied"
            )

        # Convert ObjectId to string for response
        borrower["_id"] = str(borrower["_id"])

        return custom_response(
            status.HTTP_200_OK,
            "Borrower details retrieved successfully",
           {"data" : borrower}
        )

    except Exception as e:
        return custom_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Service error: {str(e)}"
        )