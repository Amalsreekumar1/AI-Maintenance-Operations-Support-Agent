# Decides what to do with a ticket
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(equipment_id, ticket: TicketCreate, db):
    existing = check_ticket(equipment_id, db, ticket.subject)
    if existing is not None:
        return existing
    else:
        new_ticket = Ticket(
        equipment_id = equipment_id,
        subject = ticket.subject,
        description = ticket.description,
        priority = ticket.priority
        )

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)
        return new_ticket

def check_ticket(equipment_id, db, subject):
    ticket = db.query(Ticket).filter(Ticket.equipment_id == customer_id).all()

    for t in ticket:
        if t.subject == subject and t.status == TicketStatus.open:
            return t
        
    return None

def get_equipment_tickets(equipment_id, db):
    return db.query(Ticket).filter(Ticket.equipment_id == equipment_id).all()

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



