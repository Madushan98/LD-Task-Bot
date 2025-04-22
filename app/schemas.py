from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models import AssignmentStatus

class TaskCreate(BaseModel):
    description: str

class TaskResponse(BaseModel):
    id: str
    description: str
    assigned: bool
    deadline: Optional[datetime]
    completed: bool

    class Config:
        orm_mode = True

class SubmitRequest(BaseModel):
    task_id: str

class ExtensionRequest(BaseModel):
    reason: str

class TalentResponse(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

class AssignmentBase(BaseModel):
    task_id: str
    talent_id: str
    status: Optional[AssignmentStatus]
    extension_requested: Optional[bool] = False
    extension_reason: Optional[str]

class AssignmentResponse(AssignmentBase):
    id: str

    class Config:
        orm_mode = True