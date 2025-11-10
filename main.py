import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import db, create_document, get_documents
from schemas import Pressrelease, Signal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MonitorRequest(BaseModel):
    tickers: List[str]

@app.get("/")
def read_root():
    return {"message": "Stock News Monitor API"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

@app.get("/api/press")
async def list_press(ticker: Optional[str] = None, limit: int = 50):
    filt = {"ticker": ticker} if ticker else {}
    docs = get_documents("pressrelease", filt, limit)
    # Convert ObjectId and datetimes
    for d in docs:
        d["_id"] = str(d.get("_id"))
        for k in ["created_at", "updated_at", "published_at"]:
            if d.get(k) and isinstance(d[k], datetime):
                d[k] = d[k].isoformat()
    return {"items": docs}

@app.get("/api/signals")
async def list_signals(ticker: Optional[str] = None, limit: int = 50):
    filt = {"ticker": ticker} if ticker else {}
    docs = get_documents("signal", filt, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
        for k in ["created_at", "updated_at", "published_at"]:
            if d.get(k) and isinstance(d[k], datetime):
                d[k] = d[k].isoformat()
    return {"items": docs}

@app.post("/api/mock-ingest")
async def mock_ingest(req: MonitorRequest):
    # This mock endpoint simulates ingestion, analysis and signal generation
    now = datetime.utcnow()
    created = []
    for t in req.tickers:
        pr = Pressrelease(
            source="ExampleWire",
            title=f"{t} announces strategic partnership",
            url=f"https://news.example.com/{t.lower()}-partnership",
            published_at=now,
            summary=f"{t} entered a new partnership expected to expand market reach.",
            ticker=t.upper(),
            exchange="NASDAQ",
            sentiment="positive",
            sentiment_score=0.72,
        )
        create_document("pressrelease", pr)
        sig = Signal(
            ticker=t.upper(),
            action="buy",
            confidence=0.82,
            reason="Positive sentiment and growth catalyst",
            source_title=pr.title,
            source_url=pr.url,
            published_at=now,
            sentiment_score=0.72,
            sentiment_label="positive",
        )
        create_document("signal", sig)
        created.append({"ticker": t.upper(), "press_title": pr.title})
    return {"status": "ok", "created": created}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
