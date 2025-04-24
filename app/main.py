from typing import List
from fastapi import FastAPI
from app.db import engine, get_db
from app import mock_data
from app.schemas import AssignmentResponse, SubmitRequest, ExtensionRequest, TalentResponse, TaskCreate, TaskResponse
from app.models import AssignmentStatus, Base, Talent, Task, Assignment
from app.utils import serialize_embedding, get_fake_embedding
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException

import uuid

app = FastAPI()

# Create DB tables and load mock data on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    mock_data.load_data()

@app.post("/tasks")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    embedding = serialize_embedding(get_fake_embedding())
    task = Task(description=payload.description, embedding=embedding)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"message": "Task created", "task_id": task.id}

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

@app.post("/submit-task")
def submit_task(payload: SubmitRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = True
    db.commit()
    return {"message": "Task marked as completed"}

@app.patch("/assignments/{assignment_id}/extension")
def request_extension(
    assignment_id: str,
    payload: ExtensionRequest,
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.extension_requested = True
    assignment.extension_reason = payload.reason
    db.commit()

    return {"message": "Extension request submitted"}

@app.get("/assignments", response_model=List[AssignmentResponse])
def list_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).all()

@app.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: str, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@app.get("/talent", response_model=List[TalentResponse])
def get_all_talents(db: Session = Depends(get_db)):
    return db.query(Talent).all()

#mock api to create a assignment with a past deadline
@app.get("/assign-past-deadline")
def assign_past_deadline(db: Session = Depends(get_db)):
    # Get the first available talent
    talent = db.query(Talent).first()
    if not talent:
        raise HTTPException(status_code=404, detail="No talent found")

    # Create a new task with a past deadline
    task = Task(
        id=str(uuid.uuid4()),
        description="Task with past deadline",
        embedding=serialize_embedding(get_fake_embedding()),
        assigned=True,
        deadline=datetime.utcnow() - timedelta(days=1),  # deadline already passed
        completed=False,
    )
    db.add(task)
    db.commit()  # flush to get the task ID

    # Create an assignment linking the talent to the task
    assignment = Assignment(
        id=str(uuid.uuid4()),
        task_id=task.id,
        talent_id=talent.id,
        status=AssignmentStatus.assigned
    )
    db.add(assignment)
    db.commit()

    return {
        "message": "Assignment with past deadline created",
        "task_id": task.id,
        "talent_id": talent.id,
        "assignment_id": assignment.id
    }