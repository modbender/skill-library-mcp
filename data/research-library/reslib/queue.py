"""
Queue Manager for Research Library Extraction System.

Provides robust job lifecycle management with atomic state transitions,
priority support, and retry handling.
"""

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List, Callable

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    RETRY_PENDING = "retry_pending"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """
    Represents an extraction job in the queue.
    
    Attributes:
        id: Unique job identifier (database ID)
        attachment_id: ID of the attachment to process
        status: Current job status
        worker_id: ID of worker processing this job (if any)
        priority: Job priority (higher = more important)
        retry_count: Number of retry attempts
        error_message: Last error message (if failed)
        created_at: When job was created
        started_at: When processing started
        completed_at: When processing finished
        next_retry_at: When to retry (if status is retry_pending)
    """
    id: int
    attachment_id: int
    status: JobStatus = JobStatus.PENDING
    worker_id: Optional[str] = None
    priority: int = 0
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    
    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Job":
        """Create Job from database row."""
        return cls(
            id=row["id"],
            attachment_id=row["attachment_id"],
            status=JobStatus(row["status"]),
            worker_id=row.get("worker_id"),
            priority=row.get("priority", 0),
            retry_count=row.get("retry_count", 0),
            error_message=row.get("error_message"),
            created_at=row.get("created_at"),
            started_at=row.get("started_at"),
            completed_at=row.get("completed_at"),
            next_retry_at=row.get("next_retry_at"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Job to dictionary."""
        return {
            "id": self.id,
            "attachment_id": self.attachment_id,
            "status": self.status.value,
            "worker_id": self.worker_id,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "created_at": str(self.created_at) if self.created_at else None,
            "started_at": str(self.started_at) if self.started_at else None,
            "completed_at": str(self.completed_at) if self.completed_at else None,
            "next_retry_at": str(self.next_retry_at) if self.next_retry_at else None,
        }


class QueueManager:
    """
    Manages the extraction job queue lifecycle.
    
    Provides atomic operations for:
    - Enqueueing new jobs
    - Claiming jobs for processing
    - Marking jobs complete or failed
    - Retrying failed jobs
    - Monitoring queue health
    
    Thread-safe with proper locking for concurrent worker access.
    """
    
    # Exponential backoff delays for retries (seconds)
    RETRY_DELAYS = [0.5, 2.0, 10.0, 30.0, 60.0]
    
    def __init__(self, db: "ResearchDatabase"):
        """
        Initialize queue manager.
        
        Args:
            db: ResearchDatabase instance
        """
        self.db = db
        self._lock = threading.RLock()
        self._callbacks: Dict[str, List[Callable]] = {
            "job_enqueued": [],
            "job_claimed": [],
            "job_completed": [],
            "job_failed": [],
        }
    
    def on(self, event: str, callback: Callable):
        """Register callback for queue events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _emit(self, event: str, job: Job):
        """Emit event to registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                callback(job)
            except Exception as e:
                logger.error(f"Callback error for {event}: {e}")
    
    def enqueue(
        self,
        attachment_id: int,
        priority: int = 0,
        deduplicate: bool = True
    ) -> Optional[int]:
        """
        Add a job to the extraction queue.
        
        Args:
            attachment_id: ID of attachment to process
            priority: Job priority (higher = processed first)
            deduplicate: If True, skip if pending/processing job exists
        
        Returns:
            Job ID, or None if deduplicated
        """
        with self._lock:
            # Check for existing active job if deduplication enabled
            if deduplicate:
                existing = self.db.fetchone(
                    """
                    SELECT id FROM extraction_queue 
                    WHERE attachment_id = ? 
                    AND status IN ('pending', 'processing', 'retry_pending')
                    """,
                    (attachment_id,)
                )
                if existing:
                    logger.debug(
                        f"Skipping duplicate job for attachment {attachment_id}, "
                        f"existing job {existing['id']}"
                    )
                    return None
            
            # Verify attachment exists
            attachment = self.db.fetchone(
                "SELECT id FROM attachments WHERE id = ?",
                (attachment_id,)
            )
            if not attachment:
                raise ValueError(f"Attachment {attachment_id} not found")
            
            # Insert new job
            cursor = self.db.execute(
                """
                INSERT INTO extraction_queue (attachment_id, status, priority)
                VALUES (?, 'pending', ?)
                """,
                (attachment_id, priority)
            )
            job_id = cursor.lastrowid
            
            logger.info(f"Enqueued job {job_id} for attachment {attachment_id}")
            
            # Emit event
            job = self.get_job(job_id)
            if job:
                self._emit("job_enqueued", job)
            
            return job_id
    
    def enqueue_batch(
        self,
        attachment_ids: List[int],
        priority: int = 0
    ) -> List[int]:
        """
        Enqueue multiple jobs efficiently.
        
        Args:
            attachment_ids: List of attachment IDs
            priority: Priority for all jobs
        
        Returns:
            List of created job IDs
        """
        job_ids = []
        for attachment_id in attachment_ids:
            job_id = self.enqueue(attachment_id, priority)
            if job_id:
                job_ids.append(job_id)
        return job_ids
    
    def claim(self, worker_id: str) -> Optional[Job]:
        """
        Claim the next available job for processing.
        
        Uses atomic update to prevent race conditions between workers.
        Prioritizes by: priority DESC, created_at ASC (FIFO within priority)
        
        Also claims jobs that are ready for retry (next_retry_at <= now).
        
        Args:
            worker_id: Unique identifier of claiming worker
        
        Returns:
            Claimed Job, or None if queue is empty
        """
        with self._lock:
            # First, check for retry-ready jobs
            row = self.db.fetchone(
                """
                SELECT * FROM extraction_queue
                WHERE status = 'retry_pending'
                AND next_retry_at <= datetime('now')
                ORDER BY priority DESC, next_retry_at ASC
                LIMIT 1
                """,
                ()
            )
            
            # Then check pending jobs if no retry-ready jobs
            if not row:
                row = self.db.fetchone(
                    """
                    SELECT * FROM extraction_queue
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                    """,
                    ()
                )
            
            if not row:
                return None
            
            job_id = row["id"]
            
            # Atomic claim: update status and worker_id
            # Only succeeds if status hasn't changed
            cursor = self.db.execute(
                """
                UPDATE extraction_queue
                SET status = 'processing',
                    worker_id = ?,
                    started_at = datetime('now')
                WHERE id = ?
                AND status IN ('pending', 'retry_pending')
                """,
                (worker_id, job_id)
            )
            
            if cursor.rowcount == 0:
                # Race condition: another worker claimed it
                logger.debug(f"Job {job_id} claimed by another worker")
                return None
            
            job = self.get_job(job_id)
            if job:
                logger.info(f"Worker {worker_id} claimed job {job_id}")
                self._emit("job_claimed", job)
            
            return job
    
    def complete(
        self,
        job_id: int,
        extraction_time_ms: Optional[int] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Mark a job as complete.
        
        Args:
            job_id: Job ID
            extraction_time_ms: Time taken for extraction
            confidence: Extraction confidence score
        
        Returns:
            True if successfully marked complete
        """
        with self._lock:
            job = self.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            cursor = self.db.execute(
                """
                UPDATE extraction_queue
                SET status = 'complete',
                    completed_at = datetime('now'),
                    error_message = NULL
                WHERE id = ?
                AND status = 'processing'
                """,
                (job_id,)
            )
            
            if cursor.rowcount == 0:
                logger.warning(f"Could not complete job {job_id}, status may have changed")
                return False
            
            # Record metrics
            self._record_metrics(
                job_id=job_id,
                attachment_id=job.attachment_id,
                worker_id=job.worker_id,
                extraction_time_ms=extraction_time_ms,
                confidence=confidence,
                status="complete"
            )
            
            logger.info(f"Job {job_id} completed successfully")
            
            # Emit event
            job = self.get_job(job_id)
            if job:
                self._emit("job_completed", job)
            
            return True
    
    def failed(
        self,
        job_id: int,
        error_message: str,
        error_type: str = "unknown",
        max_retries: int = 3,
        extraction_time_ms: Optional[int] = None
    ) -> bool:
        """
        Mark a job as failed, potentially scheduling retry.
        
        Args:
            job_id: Job ID
            error_message: Error description
            error_type: Type of error (timeout, corruption, extractor_missing, etc.)
            max_retries: Maximum retry attempts
            extraction_time_ms: Time spent before failure
        
        Returns:
            True if successfully marked failed/retry_pending
        """
        with self._lock:
            job = self.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            new_retry_count = job.retry_count + 1
            
            # Determine if we should retry
            should_retry = (
                new_retry_count <= max_retries
                and error_type not in ("corruption", "permanent")
            )
            
            if should_retry:
                # Calculate backoff delay
                delay_index = min(new_retry_count - 1, len(self.RETRY_DELAYS) - 1)
                delay_seconds = self.RETRY_DELAYS[delay_index]
                
                # For missing extractor, use longer delay
                if error_type == "extractor_missing":
                    delay_seconds = max(delay_seconds, 30.0)
                
                next_retry = datetime.now() + timedelta(seconds=delay_seconds)
                
                cursor = self.db.execute(
                    """
                    UPDATE extraction_queue
                    SET status = 'retry_pending',
                        retry_count = ?,
                        error_message = ?,
                        next_retry_at = ?,
                        worker_id = NULL
                    WHERE id = ?
                    AND status = 'processing'
                    """,
                    (new_retry_count, error_message, next_retry.isoformat(), job_id)
                )
                
                if cursor.rowcount > 0:
                    logger.warning(
                        f"Job {job_id} failed (attempt {new_retry_count}), "
                        f"retry in {delay_seconds}s: {error_message}"
                    )
            else:
                # Max retries exceeded or permanent failure
                cursor = self.db.execute(
                    """
                    UPDATE extraction_queue
                    SET status = 'failed',
                        retry_count = ?,
                        error_message = ?,
                        completed_at = datetime('now'),
                        worker_id = NULL
                    WHERE id = ?
                    AND status = 'processing'
                    """,
                    (new_retry_count, error_message, job_id)
                )
                
                if cursor.rowcount > 0:
                    logger.error(
                        f"Job {job_id} permanently failed after {new_retry_count} attempts: "
                        f"{error_message}"
                    )
            
            if cursor.rowcount == 0:
                logger.warning(f"Could not mark job {job_id} as failed")
                return False
            
            # Record metrics
            self._record_metrics(
                job_id=job_id,
                attachment_id=job.attachment_id,
                worker_id=job.worker_id,
                extraction_time_ms=extraction_time_ms,
                confidence=None,
                status="retry_pending" if should_retry else "failed",
                error_type=error_type
            )
            
            # Emit event
            job = self.get_job(job_id)
            if job:
                self._emit("job_failed", job)
            
            return True
    
    def release(self, job_id: int) -> bool:
        """
        Release a job back to pending state (for graceful shutdown).
        
        Args:
            job_id: Job ID
        
        Returns:
            True if successfully released
        """
        with self._lock:
            cursor = self.db.execute(
                """
                UPDATE extraction_queue
                SET status = 'pending',
                    worker_id = NULL,
                    started_at = NULL
                WHERE id = ?
                AND status = 'processing'
                """,
                (job_id,)
            )
            
            if cursor.rowcount > 0:
                logger.info(f"Released job {job_id} back to pending")
                return True
            return False
    
    def cancel(self, job_id: int) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID
        
        Returns:
            True if successfully cancelled
        """
        with self._lock:
            cursor = self.db.execute(
                """
                UPDATE extraction_queue
                SET status = 'cancelled',
                    completed_at = datetime('now')
                WHERE id = ?
                AND status IN ('pending', 'retry_pending')
                """,
                (job_id,)
            )
            
            if cursor.rowcount > 0:
                logger.info(f"Cancelled job {job_id}")
                return True
            return False
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Get job by ID."""
        row = self.db.fetchone(
            "SELECT * FROM extraction_queue WHERE id = ?",
            (job_id,)
        )
        return Job.from_row(dict(row)) if row else None
    
    def get_pending_count(self) -> int:
        """Get count of pending jobs."""
        row = self.db.fetchone(
            "SELECT COUNT(*) as count FROM extraction_queue WHERE status = 'pending'"
        )
        return row["count"] if row else 0
    
    def get_processing_count(self) -> int:
        """Get count of processing jobs."""
        row = self.db.fetchone(
            "SELECT COUNT(*) as count FROM extraction_queue WHERE status = 'processing'"
        )
        return row["count"] if row else 0
    
    def get_retry_pending_count(self) -> int:
        """Get count of jobs waiting for retry."""
        row = self.db.fetchone(
            "SELECT COUNT(*) as count FROM extraction_queue WHERE status = 'retry_pending'"
        )
        return row["count"] if row else 0
    
    def get_failed_jobs(self, limit: int = 100) -> List[Job]:
        """Get failed jobs for review."""
        rows = self.db.fetchall(
            """
            SELECT * FROM extraction_queue 
            WHERE status = 'failed'
            ORDER BY completed_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [Job.from_row(dict(row)) for row in rows]
    
    def retry_failed(self, job_id: Optional[int] = None) -> int:
        """
        Reset failed jobs to pending for retry.
        
        Args:
            job_id: Specific job to retry, or None to retry all
        
        Returns:
            Number of jobs reset
        """
        with self._lock:
            if job_id:
                cursor = self.db.execute(
                    """
                    UPDATE extraction_queue
                    SET status = 'pending',
                        retry_count = 0,
                        error_message = NULL,
                        worker_id = NULL,
                        completed_at = NULL,
                        next_retry_at = NULL
                    WHERE id = ?
                    AND status = 'failed'
                    """,
                    (job_id,)
                )
            else:
                cursor = self.db.execute(
                    """
                    UPDATE extraction_queue
                    SET status = 'pending',
                        retry_count = 0,
                        error_message = NULL,
                        worker_id = NULL,
                        completed_at = NULL,
                        next_retry_at = NULL
                    WHERE status = 'failed'
                    """
                )
            
            count = cursor.rowcount
            if count > 0:
                logger.info(f"Reset {count} failed jobs to pending")
            return count
    
    def cleanup_stale_jobs(self, stale_threshold_minutes: int = 30) -> int:
        """
        Reset jobs that have been processing for too long (worker crash).
        
        Args:
            stale_threshold_minutes: Minutes before job is considered stale
        
        Returns:
            Number of jobs reset
        """
        with self._lock:
            cursor = self.db.execute(
                """
                UPDATE extraction_queue
                SET status = 'pending',
                    worker_id = NULL,
                    started_at = NULL
                WHERE status = 'processing'
                AND started_at < datetime('now', ?)
                """,
                (f"-{stale_threshold_minutes} minutes",)
            )
            
            count = cursor.rowcount
            if count > 0:
                logger.warning(f"Reset {count} stale processing jobs")
            return count
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics."""
        stats = {
            "pending": self.get_pending_count(),
            "processing": self.get_processing_count(),
            "retry_pending": self.get_retry_pending_count(),
        }
        
        # Get counts by status
        rows = self.db.fetchall(
            """
            SELECT status, COUNT(*) as count
            FROM extraction_queue
            GROUP BY status
            """
        )
        for row in rows:
            stats[f"total_{row['status']}"] = row["count"]
        
        # Get recent completion rate
        completed_24h = self.db.fetchone(
            """
            SELECT COUNT(*) as count FROM extraction_queue
            WHERE status = 'complete'
            AND completed_at > datetime('now', '-24 hours')
            """
        )
        stats["completed_24h"] = completed_24h["count"] if completed_24h else 0
        
        # Get average processing time
        avg_time = self.db.fetchone(
            """
            SELECT AVG(extraction_time_ms) as avg_time
            FROM extraction_metrics
            WHERE status = 'complete'
            AND created_at > datetime('now', '-24 hours')
            """
        )
        stats["avg_extraction_time_ms"] = (
            round(avg_time["avg_time"]) if avg_time and avg_time["avg_time"] else 0
        )
        
        return stats
    
    def _record_metrics(
        self,
        job_id: int,
        attachment_id: int,
        worker_id: Optional[str],
        extraction_time_ms: Optional[int],
        confidence: Optional[float],
        status: str,
        error_type: Optional[str] = None
    ):
        """Record extraction metrics."""
        # Get file size for metrics
        attachment = self.db.fetchone(
            "SELECT file_size FROM attachments WHERE id = ?",
            (attachment_id,)
        )
        file_size = attachment["file_size"] if attachment else None
        
        self.db.execute(
            """
            INSERT INTO extraction_metrics 
            (job_id, attachment_id, worker_id, extraction_time_ms, 
             confidence, status, error_type, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, attachment_id, worker_id, extraction_time_ms,
             confidence, status, error_type, file_size)
        )
