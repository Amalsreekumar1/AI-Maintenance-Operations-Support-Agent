# Decides what to do with a ticket
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(customer_id, ticket: TicketCreate, db):
    new_ticket = Ticket(
        customer_id = customer_id,
        subject = ticket.subject,
        description = ticket.description,
        priority = ticket.priority
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

def get_customer_tickets(customer_id, db):
    return db.query(Ticket).filter(Ticket.customer_id == customer_id).all()

def update_ticket(id, db, update: TicketUpdate):
    current_ticket = db.query(Ticket).filter(Ticket.id == id).first()
    if current_ticket is None:
        return "No ticket found"

    if update.status != None:
        current_ticket.status = update.status
        
    if update.priority != None:
        current_ticket.priority = update.priority
        
    db.commit()
    db.refresh(current_ticket)
    return current_ticket

def check_ticket():
    return 

