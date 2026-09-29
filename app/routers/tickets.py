# Handles HTTP requests
from fastapi import APIRouter, Depends
from app.database import get_db
from app.services.ticket_service import get_customer_tickets, create_ticket, update_ticket
from app.schemas.ticket import TicketCreate, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/{customer_id}")
def get_customer_ticket(customer_id : int, db = Depends(get_db)):
    return get_customer_tickets(customer_id, db)

@router.post("/")
def create_new_ticket(customer_id : int, ticket : TicketCreate, db = Depends(get_db)):
    return create_ticket(customer_id, ticket, db)

@router.patch("/{id}")
def update_new_ticket(id : int, ticket : TicketUpdate, db = Depends(get_db)):
    return update_ticket(id, db, ticket)