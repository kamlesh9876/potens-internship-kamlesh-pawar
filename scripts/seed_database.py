"""
Database seeding script for the SkillPath Recommendation API.
Adds 15+ catalogue items to the database.
Idempotent - can be run multiple times safely.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.item import Item
from app.models.user import User
from app.core.security import get_password_hash


def seed_items(db: Session) -> None:
    """Seed catalogue items"""
    items_data = [
        {
            "name": "Python Bootcamp",
            "category": "Programming",
            "price": 99.99,
            "skill_level": "Beginner",
            "goal": "Career Change",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Learn Python from scratch with hands-on projects. Covers fundamentals, data structures, and basic algorithms."
        },
        {
            "name": "Data Science with Python",
            "category": "Data Science",
            "price": 149.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Master data analysis, visualization, and machine learning using Python libraries like pandas, numpy, and scikit-learn."
        },
        {
            "name": "Full Stack Web Development",
            "category": "Web Development",
            "price": 199.99,
            "skill_level": "Beginner",
            "goal": "Career Change",
            "location": "Online",
            "pace": "Instructor-led",
            "description": "Build modern web applications using React, Node.js, and MongoDB. Includes real-world projects and portfolio building."
        },
        {
            "name": "Machine Learning Specialization",
            "category": "Data Science",
            "price": 299.99,
            "skill_level": "Advanced",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Deep dive into ML algorithms, neural networks, and deep learning. Requires strong math and programming background."
        },
        {
            "name": "Mobile App Development",
            "category": "Mobile Development",
            "price": 179.99,
            "skill_level": "Intermediate",
            "goal": "Career Change",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Build iOS and Android apps using React Native and Flutter. Cross-platform development with modern tools."
        },
        {
            "name": "Cloud Computing Fundamentals",
            "category": "Cloud Computing",
            "price": 129.99,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Introduction to AWS, Azure, and GCP. Learn cloud services, deployment, and infrastructure as code."
        },
        {
            "name": "Cybersecurity Essentials",
            "category": "Cybersecurity",
            "price": 249.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Instructor-led",
            "description": "Learn network security, ethical hacking, and security best practices. Hands-on labs and real-world scenarios."
        },
        {
            "name": "DevOps Engineering",
            "category": "DevOps",
            "price": 219.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Master CI/CD, Docker, Kubernetes, and infrastructure automation. Build and deploy scalable applications."
        },
        {
            "name": "UI/UX Design Bootcamp",
            "category": "Design",
            "price": 159.99,
            "skill_level": "Beginner",
            "goal": "Career Change",
            "location": "Online",
            "pace": "Instructor-led",
            "description": "Learn user interface and experience design. Use Figma and Adobe XD to create stunning designs."
        },
        {
            "name": "Digital Marketing Mastery",
            "category": "Marketing",
            "price": 89.99,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Master SEO, social media marketing, content marketing, and analytics. Grow your brand online."
        },
        {
            "name": "Blockchain Development",
            "category": "Blockchain",
            "price": 329.99,
            "skill_level": "Advanced",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Build decentralized applications using Solidity and Ethereum. Smart contracts and Web3 integration."
        },
        {
            "name": "Game Development with Unity",
            "category": "Game Development",
            "price": 189.99,
            "skill_level": "Intermediate",
            "goal": "Career Change",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Create 2D and 3D games using Unity and C#. Learn game physics, animations, and multiplayer systems."
        },
        {
            "name": "Project Management Professional",
            "category": "Management",
            "price": 199.99,
            "skill_level": "Beginner",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Instructor-led",
            "description": "Prepare for PMP certification. Learn Agile, Scrum, and project management methodologies."
        },
        {
            "name": "Artificial Intelligence for Business",
            "category": "AI/ML",
            "price": 279.99,
            "skill_level": "Intermediate",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Apply AI and ML to business problems. Learn about AI strategy, implementation, and ethics."
        },
        {
            "name": "React Native for Mobile",
            "category": "Mobile Development",
            "price": 169.99,
            "skill_level": "Intermediate",
            "goal": "Career Change",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Build cross-platform mobile apps with React Native. JavaScript and React knowledge required."
        },
        {
            "name": "Advanced JavaScript Patterns",
            "category": "Programming",
            "price": 119.99,
            "skill_level": "Advanced",
            "goal": "Career Growth",
            "location": "Online",
            "pace": "Self-paced",
            "description": "Master advanced JavaScript concepts, design patterns, and performance optimization."
        }
    ]
    
    for item_data in items_data:
        # Check if item already exists
        existing = db.query(Item).filter(Item.name == item_data["name"]).first()
        if not existing:
            item = Item(**item_data)
            db.add(item)
    
    db.commit()
    print(f"[OK] Seeded {len(items_data)} catalogue items")


def seed_users(db: Session) -> None:
    """Seed admin user"""
    # Check if admin exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("[OK] Created admin user (username: admin, password: admin123)")
    else:
        print("[OK] Admin user already exists")


def main():
    """Main seeding function"""
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        seed_items(db)
        seed_users(db)
        print("\n[OK] Database seeding completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
