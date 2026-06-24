from app.database import Base, SessionLocal, engine
from app.schemas.admin import ContentCreateRequest
from app.services.admin import AdminService


SEED_CONTENTS = [
    {
        "title": "一年级识字阅读自测表",
        "content_type": "pdf",
        "subject": "语文",
        "problem": "识字阅读",
        "target_age_min": 6,
        "target_age_max": 8,
        "grade": "一年级",
        "summary": "帮助家长快速判断孩子识字量和阅读基础。",
        "file_path": "materials/reading-checklist.pdf",
        "next_action": "测评",
        "next_action_url": "/assessment/reading",
        "tags": ["一年级", "语文", "识字阅读"],
    },
    {
        "title": "7天专注力打卡表",
        "content_type": "pdf",
        "subject": "专注力",
        "problem": "注意力不集中",
        "target_age_min": 5,
        "target_age_max": 8,
        "grade": None,
        "summary": "用每日短任务帮助孩子建立学习专注节奏。",
        "file_path": "materials/focus-7-days.pdf",
        "next_action": "训练营",
        "next_action_url": "/camp/focus",
        "tags": ["专注力", "打卡", "训练营"],
    },
    {
        "title": "一年级数学计算练习包",
        "content_type": "pdf",
        "subject": "数学",
        "problem": "计算能力",
        "target_age_min": 6,
        "target_age_max": 8,
        "grade": "一年级",
        "summary": "覆盖基础口算和应用题的家庭练习资料。",
        "file_path": "materials/math-practice.pdf",
        "next_action": "领取方案",
        "next_action_url": "/plans/math",
        "tags": ["一年级", "数学", "计算"],
    },
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        service = AdminService(db)
        for item in SEED_CONTENTS:
            payload = ContentCreateRequest(**item)
            content = service.create_content(payload)
            service.publish_content(content.id, True)
        print(f"seeded {len(SEED_CONTENTS)} contents")
    finally:
        db.close()


if __name__ == "__main__":
    main()

