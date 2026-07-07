import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "recommendation.db"

ITEMS = [
    ("LaunchPad Bootcamp", "course", 120.0, "beginner", "career-switch", "remote", "steady", "Structured beginner course with coaching."),
    ("Career Pivot Accelerator", "bootcamp", 180.0, "beginner", "career-switch", "remote", "steady", "Career switch bootcamp with mentoring."),
    ("Data Storytelling Clinic", "workshop", 110.0, "beginner", "career-switch", "remote", "steady", "Learn to communicate insights clearly."),
    ("AI Foundations", "course", 180.0, "beginner", "build-ai", "remote", "steady", "Accessible AI course for first-time builders."),
    ("Prompt Engineering Lab", "workshop", 140.0, "intermediate", "build-ai", "remote", "fast", "Lab-based prompt engineering practice."),
    ("Machine Learning Basics", "course", 260.0, "intermediate", "build-ai", "remote", "steady", "Practical ML foundations for professionals."),
    ("Design Systems Lab", "workshop", 90.0, "beginner", "portfolio", "onsite", "steady", "Hands-on workshop to strengthen a portfolio."),
    ("UX Research Sprint", "bootcamp", 160.0, "beginner", "portfolio", "hybrid", "fast", "Intensive design research sprint."),
    ("UI Systems Workshop", "workshop", 95.0, "beginner", "portfolio", "remote", "steady", "Rapid UI systems workshop for portfolio projects."),
    ("Leadership Essentials", "course", 210.0, "intermediate", "leadership", "onsite", "steady", "Foundational leadership course for rising managers."),
    ("Executive Presence Lab", "mentoring", 320.0, "advanced", "leadership", "remote", "fast", "Executive coaching for high-growth leaders."),
    ("Growth Analytics Masterclass", "course", 220.0, "intermediate", "growth", "remote", "steady", "A practical analytics course for growth teams."),
    ("Growth Product Academy", "course", 280.0, "advanced", "growth", "remote", "steady", "Advanced growth product curriculum for experienced operators."),
    ("Product Strategy Studio", "mentoring", 300.0, "advanced", "leadership", "remote", "steady", "Leadership coaching for senior product managers."),
    ("Data Sprint", "bootcamp", 250.0, "intermediate", "career-switch", "hybrid", "fast", "Fast-paced data skills bootcamp for career switchers."),
]


def seed_catalogue():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            skill_level TEXT NOT NULL,
            goal TEXT NOT NULL,
            location TEXT NOT NULL,
            pace TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    conn.execute("DELETE FROM items")
    conn.execute('DELETE FROM sqlite_sequence WHERE name = "items"')
    conn.executemany(
        "INSERT INTO items (name, category, price, skill_level, goal, location, pace, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ITEMS,
    )
    conn.commit()
    conn.close()
    print(f"Seeded {len(ITEMS)} items into {DB_PATH}")


if __name__ == "__main__":
    seed_catalogue()
