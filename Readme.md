# Task-bot – Smart Task Assignment with AI

**Task-bot** is a Fast API + Celery-based automation system that assigns tasks to the most suitable talent using AI-driven profile matching and handles deadlines, extension requests, and task reassignments intelligently.

---

## 🔧 Features

- 🧠 **Smart Matching**  
  Assigns tasks using cosine similarity between task descriptions and LinkedIn/LD profile embeddings.

- ⏳ **24-Hour Deadline**  
  Automatically gives talent a fixed 24-hour window to complete the assigned task.

- 📬 **Extension Requests**  
  Allows talents to request deadline extensions with a reason.

- 🤖 **AI Review**  
  Leverages Gemini to evaluate extension requests based on the reason and the availability of other talent.

- 🔁 **Auto-Reassign**  
  Automatically reassigns the task if:
  - No extension is requested after the deadline.
  - The extension request is rejected.

- ✅ **Completion Tracking**  
  Marks the task as complete once the assigned talent submits their work.

---

## 🛠 Tech Stack

- Python 3.x
- Celery (with Redis or RabbitMQ)
- SQLAlchemy or any ORM of your choice
- Gemini API for natural language reasoning
- Cron scheduling (via Celery Beat or external scheduler)



## 🚀 Getting Started

```bash
# Clone the repo

# Install dependencies
pip install -r requirements.txt

# Start Redis (or RabbitMQ)
docker run -d -p 6379:6379 redis

# Start Celery worker
celery -A app worker --loglevel=info

# Start Celery beat (for scheduled task checking)
celery -A app beat --loglevel=info
