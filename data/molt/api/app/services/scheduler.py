"""Background scheduler for polling campaign balances."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.services.balance_tracker import BalanceTracker


scheduler = AsyncIOScheduler()


async def poll_balances_job():
    """Background job to poll all active campaign balances."""
    async with AsyncSessionLocal() as db:
        tracker = BalanceTracker(db)
        await tracker.poll_all_active_campaigns()


def start_scheduler():
    """Start the background scheduler."""
    if scheduler.running:
        return
    
    interval_seconds = settings.balance_poll_interval_seconds
    scheduler.add_job(
        poll_balances_job,
        trigger=IntervalTrigger(seconds=interval_seconds),
        id="poll_balances",
        name="Poll campaign balances",
        replace_existing=True,
    )
    scheduler.start()


def shutdown_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
