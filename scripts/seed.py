import sqlite3
from pathlib import Path
import sys
import os
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import DATABASE_URL


def get_db_path():
    """Extract database path from DATABASE_URL"""
    db_url = DATABASE_URL
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "")
    return db_url


def run_migrations():
    """Run Alembic migrations to create/update database schema"""
    print("Running database migrations...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Migration failed: {result.stderr}")
        return False
    print("Migrations completed successfully")
    return True


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
    """Seed the database with sample items"""
    # Run migrations first
    if not run_migrations():
        print("Failed to run migrations, aborting seed")
        return
    
    DB_PATH = Path(get_db_path())
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM items")
    # Reset auto-increment if sqlite_sequence exists
    try:
        conn.execute("DELETE FROM sqlite_sequence WHERE name='items'")
    except sqlite3.OperationalError:
        # sqlite_sequence table doesn't exist, skip
        pass
    conn.executemany(
        "INSERT INTO items (name, category, price, skill_level, goal, location, pace, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ITEMS,
    )
    conn.commit()
    conn.close()
    print(f"Seeded {len(ITEMS)} items into {DB_PATH}")


def cleanup_catalogue():
    """Remove all items from the database"""
    DB_PATH = Path(get_db_path())
    if not DB_PATH.exists():
        print(f"Database {DB_PATH} does not exist")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM items")
    conn.execute('DELETE FROM sqlite_sequence WHERE name = "items"')
    conn.commit()
    conn.close()
    print(f"Cleaned up all items from {DB_PATH}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database seed script")
    parser.add_argument("--cleanup", action="store_true", help="Clean up database instead of seeding")
    parser.add_argument("--migrate-only", action="store_true", help="Only run migrations without seeding")
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_catalogue()
    elif args.migrate_only:
        run_migrations()
    else:
        seed_catalogue()
