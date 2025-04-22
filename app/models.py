import enum
from sqlalchemy import Column, Enum, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class Talent(Base):
    __tablename__ = 'talent'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    embedding = Column(String)

    assignments = relationship("Assignment", back_populates="talent")

class Task(Base):
    __tablename__ = 'task'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    description = Column(String)
    embedding = Column(String)
    assigned = Column(Boolean, default=False)
    deadline = Column(DateTime)
    completed = Column(Boolean, default=False)

    assignments = relationship("Assignment", back_populates="task")

class AssignmentStatus(str, enum.Enum):
    assigned = "assigned"
    completed = "completed"
    failed = "failed"

class Assignment(Base):
    __tablename__ = 'assignment'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('task.id'))
    talent_id = Column(String, ForeignKey('talent.id'))
    extension_requested = Column(Boolean, default=False)
    extension_reason = Column(String, default="")
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.assigned)

    task = relationship("Task", back_populates="assignments")
    talent = relationship("Talent", back_populates="assignments")