from app.db import SessionLocal
from app.models import Task, Talent
from app.utils import get_fake_embedding, serialize_embedding

def load_data():
    db = SessionLocal()
       # Add talents if none exist
    if not db.query(Talent).first():
        for i in range(3):
            embedding = serialize_embedding(get_fake_embedding())
            db.add(Talent(name=f"Talent {i+1}", embedding=embedding))

    # Add tasks if none exist
    if not db.query(Task).first():
        for i in range(2):
            embedding = serialize_embedding(get_fake_embedding())
            db.add(Task(description=f"Task {i+1} description", embedding=embedding))

    
    db.commit()
    db.close()
