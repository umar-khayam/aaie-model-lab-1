from fastapi import FastAPI
from app.api.v2 import feedback

app = FastAPI(title="FastAPI Feedback Generator v2")

# Include API v2 router
app.include_router(feedback.router)

@app.get("/")
def root():
    return {"message": "FastAPI Feedback Generator v2 is running."}
