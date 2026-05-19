"""
main.py
========
FastAPI backend for the Pakistan Service Orchestrator.
Exposes the orchestration pipeline as a REST API for mobile/web clients.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

# Import the core logic from our orchestrator
from orchestrate_service_request import orchestrate

app = FastAPI(
    title="Pakistan Service Orchestrator API",
    description="Backend API for intent parsing, provider discovery, and booking simulation.",
    version="1.0.0"
)

# Enable CORS for Flutter/Web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ServiceRequest(BaseModel):
    user_input: str
    user_name: str = "Customer"
    user_phone: str = "+92-300-0000000"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pakistan Service Orchestrator API 🇵🇰"}

@app.post("/api/orchestrate")
def orchestrate_request(request: ServiceRequest) -> Dict[str, Any]:
    """
    Runs the full orchestration pipeline (Intent -> Discovery -> Booking)
    and returns the structured JSON response.
    """
    # Call the existing orchestration logic
    result = orchestrate(
        user_request=request.user_input,
        user_name=request.user_name,
        user_phone=request.user_phone
    )
    
    # Check if there was an error at any step
    if "error" in result:
        return {"status": "error", "message": result["error"], "data": result}
        
    # If the pipeline failed to find providers or parse intent (handled loosely in orchestrate)
    if not result.get("intent", {}).get("service_type"):
        return {"status": "error", "message": "Could not understand service request.", "data": result}
        
    if not result.get("discovery", {}).get("ranked_providers"):
        return {"status": "error", "message": "No providers found for this request.", "data": result}

    return {"status": "success", "data": result}

if __name__ == "__main__":
    import uvicorn
    # Run the server on localhost:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
