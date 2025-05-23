from fastapi import FastAPI
from routes import auth, borrower, transaction
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from services.auth import get_current_user
from utils.comman import  validation_exception_handler
from fastapi.exceptions import RequestValidationError
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:3000",  # your Next.js dev server
    "https://simple-lender.vercel.app/"  # your production domain
    "http://localhost:3002"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API with custom JWT auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }


    for route in app.routes:
        if isinstance(route, APIRoute):
            for dependency in route.dependant.dependencies:
                if dependency.call == get_current_user:
                    path = route.path
                    method = list(route.methods)[0].lower()
                    if "security" not in openapi_schema["paths"][path][method]:
                        openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.openapi = custom_openapi

app.include_router(auth.router, prefix="/api/auth")
app.include_router(borrower.router, prefix="/api/borrower")
app.include_router(transaction.router, prefix="/api/transaction")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))  # Render sets $PORT dynamically
    uvicorn.run("main:app", host="0.0.0.0", port=port)
