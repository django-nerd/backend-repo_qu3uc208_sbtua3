import os
from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Booking, ContactMessage, Court

app = FastAPI(title="Pickleball Venue API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Pickleball Venue Backend is running"}

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
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Public data: list courts
@app.get("/api/courts", response_model=List[Court])
def list_courts():
    try:
        items = get_documents("court", {}) if db else []
        result = []
        for item in items:
            result.append(Court(
                name=item.get("name", "Court"),
                surface=item.get("surface"),
                indoor=item.get("indoor", False)
            ))
        return result
    except Exception:
        return []

class AvailabilityQuery(BaseModel):
    date: date
    court_id: Optional[str] = None

@app.post("/api/availability")
def check_availability(payload: AvailabilityQuery):
    # Simple availability check: return suggested hourly slots 7-22 with booked flags
    try:
        booked = []
        if db:
            booked_docs = get_documents(
                "booking",
                {"booking_date": payload.date.isoformat(), **({"court_id": payload.court_id} if payload.court_id else {})}
            )
            for b in booked_docs:
                booked.append({"time_slot": b.get("time_slot"), "court_id": b.get("court_id")})
        slots = [f"{h:02d}:00-{h+1:02d}:00" for h in range(7, 22)]
        return {
            "date": payload.date.isoformat(),
            "court_id": payload.court_id,
            "slots": [
                {"time_slot": s, "booked": any(x["time_slot"] == s for x in booked)} for s in slots
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/book")
def create_booking(booking: Booking):
    try:
        # Prevent double-booking for same court + time
        if db:
            existing = get_documents(
                "booking",
                {
                    "booking_date": booking.booking_date.isoformat(),
                    "time_slot": booking.time_slot,
                    "court_id": booking.court_id,
                },
            )
            if existing:
                raise HTTPException(status_code=409, detail="This time slot is already booked.")
            booking_id = create_document("booking", booking)
            return {"ok": True, "id": booking_id}
        # If DB missing, simulate success (non-persistent)
        return {"ok": True, "id": "dev-simulated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contact")
def contact(msg: ContactMessage):
    try:
        if db:
            message_id = create_document("contactmessage", msg)
            return {"ok": True, "id": message_id}
        return {"ok": True, "id": "dev-simulated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
