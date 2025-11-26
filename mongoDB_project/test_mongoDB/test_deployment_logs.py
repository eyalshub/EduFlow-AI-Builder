import asyncio
from datetime import datetime
from mongoDB_project.config.connection import db
from app.models import deployment_logs

example_log = {
    "_id": "deploy_log_98765",
    "timestamp": datetime.utcnow().isoformat(),
    "outlineId": "bp_lesson_id_FINAL",
    "targetLms": "Amit_LMS_Production",
    "status": "Success",
    "lmsCourseId": "LMS_COURSE_ID_1138",
    "errorLog": None
}

async def run():
    # Check if log already exists
    existing = await db["deployment_logs"].find_one({"_id": example_log["_id"]})
    if not existing:
        await deployment_logs.insert_deployment_log(example_log)
    else:
        print("📄 Log already exists.")

    print("\n📋 All logs:")
    logs = await deployment_logs.get_all_deployment_logs()
    for log in logs:
        print(log)

    print("\n✅ Success logs:")
    success_logs = await deployment_logs.get_logs_by_status("Success")
    for log in success_logs:
        print(log)

    print("\n📛 Failed deployments:")
    failed_logs = await deployment_logs.get_failed_deployments()
    for log in failed_logs:
        print(log)

if __name__ == "__main__":
    asyncio.run(run())
