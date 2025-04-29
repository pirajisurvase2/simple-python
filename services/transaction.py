from fastapi import HTTPException, status
from bson import ObjectId
from database import transactions_collection, borrower_collection
from model.transaction import TransactionModel
from utils.comman import custom_response, custom_pagination_response
from datetime import datetime, date
from utils.comman import serialize_mongo_documents

def calculate_transaction_fields(txn: dict):
    principal = txn["principal_amount"]
    rate = txn["interest_value"]
    interest = (rate / 100) * principal if txn["interest_type"] == "percentage" else rate
    total = principal + interest
    return {
        "adjusted_principal": principal,
        "interest_amount": interest,
        "total_balance": total
    }

async def verify_borrower_ownership(borrower_id: str, lender_id: str):
    borrower = await borrower_collection.find_one({
        "_id": ObjectId(borrower_id),
        "lender_id": lender_id
    })
    if not borrower:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized or borrower not found")
    return borrower

async def add_transaction_service(txn_data: TransactionModel, current_user: dict):
    await verify_borrower_ownership(txn_data.borrower_id, current_user["_id"])

    txn_dict = txn_data.dict()
    txn_dict.update(calculate_transaction_fields(txn_dict))
    txn_dict.update({
        "status": "active",
        "lender_id": current_user["_id"]
    })
    if isinstance(txn_dict.get('transaction_date'), date):
        txn_dict['transaction_date'] = datetime.combine(txn_dict['transaction_date'], datetime.min.time())

    await transactions_collection.insert_one(txn_dict)
    return custom_response(201, "Transaction added")

async def update_transaction_service(txn_id: str, txn_data: TransactionModel, current_user: dict):
    txn = await transactions_collection.find_one({"_id": ObjectId(txn_id)})
    if not txn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    await verify_borrower_ownership(txn["borrower_id"], current_user["_id"])

    txn_dict = txn_data.dict()
    if isinstance(txn_dict.get('transaction_date'), date):
        txn_dict['transaction_date'] = datetime.combine(txn_dict['transaction_date'], datetime.min.time())

    txn_dict.update(calculate_transaction_fields(txn_dict))

    await transactions_collection.update_one(
        {"_id": ObjectId(txn_id)},
        {"$set": txn_dict}
    )
    return custom_response(200, "Transaction updated")

async def delete_transaction_service(txn_id: str, current_user: dict):
    txn = await transactions_collection.find_one({"_id": ObjectId(txn_id)})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await verify_borrower_ownership(txn["borrower_id"], current_user["_id"])

    await transactions_collection.delete_one({"_id": ObjectId(txn_id)})
    return custom_response(200, "Transaction deleted")

async def list_transactions_service(page: int, limit: int, borrower_name: str, email: str, status: str, sort_by: str, current_user: dict):
    skip = (page - 1) * limit
    query = {}

    borrower_filter = {"lender_id": current_user["_id"]}
    if borrower_name:
        borrower_filter["name"] = {"$regex": borrower_name, "$options": "i"}
    if email:
        borrower_filter["email"] = {"$regex": email, "$options": "i"}

    borrowers = await borrower_collection.find(borrower_filter).to_list(None)
    borrower_ids = [str(b["_id"]) for b in borrowers]

    query["borrower_id"] = {"$in": borrower_ids}
    if status:
        query["status"] = status

    total_count = await transactions_collection.count_documents(query)
    txns = await transactions_collection.find(query).sort(sort_by, -1).skip(skip).limit(limit).to_list(length=limit)

    borrower_map = {str(b["_id"]): f"{b.get('first_name', '')} {b.get('last_name', '')}".strip() for b in borrowers}

    for txn in txns:
        txn["borrower_name"] = borrower_map.get(txn["borrower_id"], "N/A")
    
    txns = serialize_mongo_documents(txns)

    return custom_response(200, "Transaction list fetched", {
        "data": custom_pagination_response(page, limit, total_count, txns)
    })
