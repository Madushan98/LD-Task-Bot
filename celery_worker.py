from celery import Celery
from celery.schedules import crontab
from app.db import SessionLocal
from app.models import AssignmentStatus, Task, Talent, Assignment
from app.utils import deserialize_embedding, should_approve_extension
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta

app = Celery("celery_task_assigner", broker="redis://localhost:6379/0")

app.conf.beat_schedule = {
    "assign-task-every-1-minutes": {
        "task": "celery_worker.assign_task",
        "schedule": crontab(),
    },
     "evaluate-extension-requests-every-1-minutes": {
        "task": "celery_worker.evaluate_pending_extensions",
        "schedule": crontab(),
    },
     "unassign_expired_tasks": {
        "task": "celery_worker.unassign_expired_tasks",
        "schedule": crontab(),
    },
}

app.conf.timezone = "UTC"

@app.task(name="celery_worker.assign_task")
def assign_task():
    db = SessionLocal()
    try:
        # Get tasks that are not currently assigned
        unassigned_tasks = db.query(Task).filter_by(assigned=False, completed=False).all()
        print(f"Unassigned tasks: {[task.id for task in unassigned_tasks]}")
        talents = db.query(Talent).all()

        for task in unassigned_tasks:
            task_vec = deserialize_embedding(task.embedding)

            # Get all failed talent IDs for this task
            failed_talent_ids = {
                a.talent_id for a in db.query(Assignment).filter(
                    Assignment.task_id == task.id,
                    Assignment.status.in_([AssignmentStatus.failed])
                )
            }

            best_match = None
            best_score = -1

            for talent in talents:
                if talent.id in failed_talent_ids:
                    continue  # Skip failed or currently assigned talents

                talent_vec = deserialize_embedding(talent.embedding)
                score = cosine_similarity([task_vec], [talent_vec])[0][0]

                if score > best_score:
                    best_score = score
                    best_match = talent

            print(f"Best score for task {task.id}: {best_score}")

            if best_match and best_score > 0.75:
                new_assignment = Assignment(
                    task_id=task.id,
                    talent_id=best_match.id,
                    status=AssignmentStatus.assigned
                )
                task.assigned = True
                task.deadline = datetime.utcnow() + timedelta(hours=24)
                db.add(new_assignment)

        db.commit()
    finally:
        db.close()

@app.task(name="celery_worker.evaluate_pending_extensions")
def evaluate_pending_extensions():
    db = SessionLocal()
    try:
        pending_assignments = db.query(Assignment).filter(Assignment.extension_requested == True).all()
        talents = db.query(Talent).all()

        for assignment in pending_assignments:
            task = db.query(Task).filter(Task.id == assignment.task_id).first()
            if not task:
                continue

            reason = assignment.extension_reason or "No reason provided"
            is_other_talent_available = len(talents) > 1

            approved = should_approve_extension(reason, is_other_talent_available)

            if approved:
                task.deadline = task.deadline + timedelta(hours=24)
                result = "approved"
            else:
                task.assigned = False
                result = "rejected"

            assignment.extension_requested = False  # reset regardless
            assignment.extension_reason= ''
            print(f"[EXTENSION {result.upper()}] Task {task.id} reassigned={not approved}")

        db.commit()
    finally:
        db.close()

@app.task(name="celery_worker.unassign_expired_tasks")
def unassign_expired_tasks():
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # Get all tasks that are currently assigned and not completed
        in_progress_tasks = db.query(Task).filter(
            Task.assigned == True,
            Task.completed == False,
            Task.deadline < now  # deadline passed
        ).all()

        for task in in_progress_tasks:
            # Find the current active assignment
            assignment = db.query(Assignment).filter(
                Assignment.task_id == task.id,
                Assignment.status == AssignmentStatus.assigned
            ).first()

            if assignment:
                assignment.status = AssignmentStatus.failed
                task.assigned = False
                db.add(assignment)

        db.commit()
    finally:
        db.close()


