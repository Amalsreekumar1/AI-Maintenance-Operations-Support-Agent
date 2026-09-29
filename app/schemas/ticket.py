#
from pydantic import BaseModel
from app.models.ticket import TicketPriority, TicketStatus

class TicketCreate(BaseModel):
    subject : str
    description : str
    priority : TicketPriority = TicketPriority.medium

class TicketUpdate(BaseModel):
    status : TicketStatus | None = None
    priority : TicketPriority | None = None