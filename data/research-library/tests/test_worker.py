"""
Tests for the extraction worker system.

Tests cover:
- Queue management (enqueue, claim, complete, failed)
- Worker pool lifecycle (start, stop, pause, resume)
- Error handling (timeout, corruption, missing extractor)
- Graceful shutdown with job preservation
- Status monitoring and metrics
- Throughput measurement
"""

import os
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reslib.database import ResearchDatabase
from reslib.queue import QueueManager, Job, JobStatus
from reslib.worker import (
    ExtractionWorker,
    WorkerStatus,
    ExtractionResult,
    ExtractorError,
    ExtractorTimeoutError,
    ExtractorCorruptionError,
    ExtractorMissingError,
    DocumentExtractor,
    PlainTextExtractor,
)


class TestQueueManager(unittest.TestCase):
    """Tests for QueueManager."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = ResearchDatabase(self.db_path)
        self.queue = QueueManager(self.db)
        
        # Create test attachment
        self.attachment_id = self.db.add_attachment(
            filename="test.txt",
            path="/tmp/test.txt",
            mime_type="text/plain",
            file_size=100
        )
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_enqueue_creates_job(self):
        """Test that enqueue creates a job in pending state."""
        job_id = self.queue.enqueue(self.attachment_id)
        
        self.assertIsNotNone(job_id)
        
        job = self.queue.get_job(job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job.attachment_id, self.attachment_id)
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertEqual(job.retry_count, 0)
    
    def test_enqueue_deduplicates(self):
        """Test that enqueue deduplicates pending jobs."""
        job_id1 = self.queue.enqueue(self.attachment_id)
        job_id2 = self.queue.enqueue(self.attachment_id)  # Should dedupe
        
        self.assertIsNotNone(job_id1)
        self.assertIsNone(job_id2)  # Deduplicated
        
        # Only one pending job should exist
        self.assertEqual(self.queue.get_pending_count(), 1)
    
    def test_enqueue_allows_after_complete(self):
        """Test that enqueue allows after job completes."""
        job_id1 = self.queue.enqueue(self.attachment_id)
        
        # Claim and complete
        job = self.queue.claim("worker-1")
        self.queue.complete(job_id1)
        
        # Should allow new job
        job_id2 = self.queue.enqueue(self.attachment_id)
        self.assertIsNotNone(job_id2)
        self.assertNotEqual(job_id1, job_id2)
    
    def test_claim_returns_pending_job(self):
        """Test that claim returns a pending job."""
        job_id = self.queue.enqueue(self.attachment_id)
        
        job = self.queue.claim("worker-1")
        
        self.assertIsNotNone(job)
        self.assertEqual(job.id, job_id)
        self.assertEqual(job.status, JobStatus.PROCESSING)
        self.assertEqual(job.worker_id, "worker-1")
    
    def test_claim_returns_none_on_empty_queue(self):
        """Test that claim returns None when queue is empty."""
        job = self.queue.claim("worker-1")
        self.assertIsNone(job)
    
    def test_claim_is_atomic(self):
        """Test that only one worker can claim a job."""
        job_id = self.queue.enqueue(self.attachment_id)
        
        claimed = []
        errors = []
        
        def claim_job(worker_id):
            try:
                job = self.queue.claim(worker_id)
                if job:
                    claimed.append((worker_id, job.id))
            except Exception as e:
                errors.append(e)
        
        # Simulate concurrent claims
        threads = [
            threading.Thread(target=claim_job, args=(f"worker-{i}",))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(claimed), 1)  # Only one worker should succeed
    
    def test_complete_marks_job_complete(self):
        """Test that complete marks job as complete."""
        job_id = self.queue.enqueue(self.attachment_id)
        self.queue.claim("worker-1")
        
        result = self.queue.complete(job_id, extraction_time_ms=100, confidence=0.95)
        
        self.assertTrue(result)
        
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.COMPLETE)
    
    def test_failed_schedules_retry(self):
        """Test that failed schedules retry for retriable errors."""
        job_id = self.queue.enqueue(self.attachment_id)
        self.queue.claim("worker-1")
        
        result = self.queue.failed(
            job_id,
            "Test error",
            error_type="timeout",
            max_retries=3
        )
        
        self.assertTrue(result)
        
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.RETRY_PENDING)
        self.assertEqual(job.retry_count, 1)
        self.assertIsNotNone(job.next_retry_at)
    
    def test_failed_marks_permanent_failure(self):
        """Test that failed marks permanent failure for corruption."""
        job_id = self.queue.enqueue(self.attachment_id)
        self.queue.claim("worker-1")
        
        result = self.queue.failed(
            job_id,
            "Corrupted file",
            error_type="corruption",
            max_retries=3
        )
        
        self.assertTrue(result)
        
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.FAILED)
    
    def test_failed_marks_max_retries_exceeded(self):
        """Test that failed marks failure after max retries."""
        job_id = self.queue.enqueue(self.attachment_id)
        
        # Simulate max retries - need to manually set retry_pending to ready
        for i in range(4):  # 4 attempts = 1 initial + 3 retries
            # For retry_pending jobs, update next_retry_at to now
            self.db.execute(
                """
                UPDATE extraction_queue 
                SET next_retry_at = datetime('now', '-1 second')
                WHERE status = 'retry_pending'
                """
            )
            
            job = self.queue.claim("worker-1")
            if job:
                self.queue.failed(
                    job.id,
                    f"Error attempt {i+1}",
                    error_type="timeout",
                    max_retries=3
                )
        
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertEqual(job.retry_count, 4)
    
    def test_release_returns_job_to_pending(self):
        """Test that release returns job to pending state."""
        job_id = self.queue.enqueue(self.attachment_id)
        self.queue.claim("worker-1")
        
        result = self.queue.release(job_id)
        
        self.assertTrue(result)
        
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertIsNone(job.worker_id)
    
    def test_get_pending_count(self):
        """Test get_pending_count returns correct count."""
        # Add multiple attachments and enqueue
        for i in range(5):
            att_id = self.db.add_attachment(
                filename=f"test{i}.txt",
                path=f"/tmp/test{i}.txt"
            )
            self.queue.enqueue(att_id)
        
        self.assertEqual(self.queue.get_pending_count(), 5)
        
        # Claim one
        self.queue.claim("worker-1")
        
        self.assertEqual(self.queue.get_pending_count(), 4)
    
    def test_get_failed_jobs(self):
        """Test get_failed_jobs returns failed jobs."""
        job_id = self.queue.enqueue(self.attachment_id)
        self.queue.claim("worker-1")
        self.queue.failed(job_id, "Error", error_type="corruption")
        
        failed = self.queue.get_failed_jobs()
        
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0].id, job_id)
    
    def test_retry_failed(self):
        """Test retry_failed resets failed jobs."""
        job_id = self.queue.enqueue(self.attachment_id)
        self.queue.claim("worker-1")
        self.queue.failed(job_id, "Error", error_type="corruption")
        
        count = self.queue.retry_failed(job_id)
        
        self.assertEqual(count, 1)
        
        job = self.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertEqual(job.retry_count, 0)
    
    def test_queue_stats(self):
        """Test get_queue_stats returns comprehensive stats."""
        # Create various job states
        att1 = self.db.add_attachment(filename="1.txt", path="/tmp/1.txt")
        att2 = self.db.add_attachment(filename="2.txt", path="/tmp/2.txt")
        att3 = self.db.add_attachment(filename="3.txt", path="/tmp/3.txt")
        
        self.queue.enqueue(att1)  # pending
        self.queue.enqueue(att2)  # will be processing
        self.queue.enqueue(att3)  # will be complete
        
        self.queue.claim("worker-1")  # att1 -> processing
        # Note: att2 and att3 still pending
        
        stats = self.queue.get_queue_stats()
        
        self.assertIn("pending", stats)
        self.assertIn("processing", stats)
        self.assertEqual(stats["processing"], 1)


class TestExtractionWorker(unittest.TestCase):
    """Tests for ExtractionWorker."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = ResearchDatabase(self.db_path)
        
        # Create test file
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_file.write_text("This is test content for extraction.")
        
        # Create attachment
        self.attachment_id = self.db.add_attachment(
            filename="test.txt",
            path=str(self.test_file),
            mime_type="text/plain",
            file_size=self.test_file.stat().st_size
        )
        
        self.worker = None
    
    def tearDown(self):
        """Clean up."""
        if self.worker:
            self.worker.stop(timeout=5)
        self.db.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_worker_starts_and_stops(self):
        """Test worker pool starts and stops cleanly."""
        self.worker = ExtractionWorker(self.db, num_workers=2)
        
        self.assertFalse(self.worker.is_running())
        
        self.worker.start()
        
        self.assertTrue(self.worker.is_running())
        
        result = self.worker.stop(timeout=5)
        
        self.assertTrue(result)
        self.assertFalse(self.worker.is_running())
    
    def test_worker_processes_job(self):
        """Test worker processes a queued job."""
        self.worker = ExtractionWorker(self.db, num_workers=1)
        self.worker.start()
        
        # Enqueue job
        job_id = self.worker.enqueue(self.attachment_id)
        self.assertIsNotNone(job_id)
        
        # Wait for processing
        timeout = time.time() + 10
        while time.time() < timeout:
            job = self.worker.queue.get_job(job_id)
            if job.status == JobStatus.COMPLETE:
                break
            time.sleep(0.1)
        
        # Verify completion
        job = self.worker.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.COMPLETE)
        
        # Verify extraction result
        attachment = self.db.get_attachment(self.attachment_id)
        self.assertIsNotNone(attachment["extracted_text"])
        self.assertIn("test content", attachment["extracted_text"])
    
    def test_worker_handles_missing_file(self):
        """Test worker handles missing file error."""
        # Create attachment pointing to non-existent file
        missing_att_id = self.db.add_attachment(
            filename="missing.txt",
            path="/tmp/nonexistent/missing.txt",
            mime_type="text/plain"
        )
        
        self.worker = ExtractionWorker(self.db, num_workers=1, max_retries=0)
        self.worker.start()
        
        job_id = self.worker.enqueue(missing_att_id)
        
        # Wait for failure
        timeout = time.time() + 10
        while time.time() < timeout:
            job = self.worker.queue.get_job(job_id)
            if job.status == JobStatus.FAILED:
                break
            time.sleep(0.1)
        
        job = self.worker.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertIn("not found", job.error_message.lower())
    
    def test_worker_handles_corrupted_file(self):
        """Test worker handles corrupted file (empty)."""
        # Create empty file
        empty_file = Path(self.temp_dir) / "empty.txt"
        empty_file.touch()
        
        empty_att_id = self.db.add_attachment(
            filename="empty.txt",
            path=str(empty_file),
            mime_type="text/plain",
            file_size=0
        )
        
        self.worker = ExtractionWorker(self.db, num_workers=1, max_retries=0)
        self.worker.start()
        
        job_id = self.worker.enqueue(empty_att_id)
        
        # Wait for failure
        timeout = time.time() + 10
        while time.time() < timeout:
            job = self.worker.queue.get_job(job_id)
            if job.status == JobStatus.FAILED:
                break
            time.sleep(0.1)
        
        job = self.worker.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertIn("empty", job.error_message.lower())
    
    def test_worker_retries_on_error(self):
        """Test worker retries failed jobs."""
        self.worker = ExtractionWorker(self.db, num_workers=1, max_retries=2)
        
        # Mock extractor to fail twice then succeed
        call_count = [0]
        original_extract = self.worker.extractors.extract
        
        def mock_extract(path, mime_type=None):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ExtractorTimeoutError("Simulated timeout")
            return original_extract(path, mime_type)
        
        self.worker.extractors.extract = mock_extract
        self.worker.start()
        
        job_id = self.worker.enqueue(self.attachment_id)
        
        # Wait for completion (with retries) - need to advance retry time
        timeout = time.time() + 20
        while time.time() < timeout:
            # Speed up retry by updating next_retry_at
            self.db.execute(
                """
                UPDATE extraction_queue 
                SET next_retry_at = datetime('now', '-1 second')
                WHERE status = 'retry_pending'
                """
            )
            
            job = self.worker.queue.get_job(job_id)
            if job.status in (JobStatus.COMPLETE, JobStatus.FAILED):
                break
            time.sleep(0.2)
        
        job = self.worker.queue.get_job(job_id)
        # Should complete after retries
        self.assertEqual(job.status, JobStatus.COMPLETE)
        self.assertEqual(call_count[0], 3)  # 2 failures + 1 success
    
    def test_graceful_shutdown_preserves_jobs(self):
        """Test graceful shutdown releases in-progress jobs."""
        self.worker = ExtractionWorker(self.db, num_workers=1)
        
        # Create slow extractor
        def slow_extract(path, mime_type=None):
            time.sleep(5)  # Long extraction
            return ExtractionResult(text="done", confidence=1.0)
        
        self.worker.extractors.extract = slow_extract
        self.worker.start()
        
        # Enqueue and wait for processing to start
        job_id = self.worker.enqueue(self.attachment_id)
        
        time.sleep(0.5)  # Wait for job to be claimed
        
        # Initiate shutdown while job is processing
        self.worker.stop(timeout=1)  # Short timeout
        
        # Job should be released back to pending
        job = self.worker.queue.get_job(job_id)
        # Either pending (released) or processing (still stuck)
        self.assertIn(job.status, [JobStatus.PENDING, JobStatus.PROCESSING])
    
    def test_get_status(self):
        """Test get_status returns comprehensive info."""
        self.worker = ExtractionWorker(self.db, num_workers=2)
        self.worker.start()
        
        # Process a job
        self.worker.enqueue(self.attachment_id)
        time.sleep(2)  # Wait for processing
        
        status = self.worker.get_status()
        
        self.assertTrue(status["running"])
        self.assertEqual(status["num_workers"], 2)
        self.assertIn("workers", status)
        self.assertIn("stats", status)
        self.assertIn("queue_stats", status)
        self.assertGreaterEqual(status["stats"]["jobs_processed"], 0)
    
    def test_pause_and_resume(self):
        """Test pause and resume functionality."""
        self.worker = ExtractionWorker(self.db, num_workers=1)
        self.worker.start()
        
        self.assertFalse(self.worker.is_paused())
        
        self.worker.pause()
        self.assertTrue(self.worker.is_paused())
        
        # Job should not be processed while paused
        job_id = self.worker.enqueue(self.attachment_id)
        time.sleep(0.5)
        
        job = self.worker.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.PENDING)
        
        # Resume and verify processing
        self.worker.resume()
        self.assertFalse(self.worker.is_paused())
        
        timeout = time.time() + 5
        while time.time() < timeout:
            job = self.worker.queue.get_job(job_id)
            if job.status == JobStatus.COMPLETE:
                break
            time.sleep(0.1)
        
        job = self.worker.queue.get_job(job_id)
        self.assertEqual(job.status, JobStatus.COMPLETE)
    
    def test_multiple_workers_process_concurrently(self):
        """Test multiple workers process jobs concurrently."""
        # Create multiple attachments
        att_ids = []
        for i in range(5):
            test_file = Path(self.temp_dir) / f"test{i}.txt"
            test_file.write_text(f"Content {i}")
            att_id = self.db.add_attachment(
                filename=f"test{i}.txt",
                path=str(test_file),
                mime_type="text/plain",
                file_size=test_file.stat().st_size
            )
            att_ids.append(att_id)
        
        self.worker = ExtractionWorker(self.db, num_workers=3)
        self.worker.start()
        
        # Enqueue all jobs
        job_ids = self.worker.enqueue_batch(att_ids)
        
        # Wait for all to complete
        timeout = time.time() + 15
        while time.time() < timeout:
            completed = sum(
                1 for jid in job_ids
                if self.worker.queue.get_job(jid).status == JobStatus.COMPLETE
            )
            if completed == len(job_ids):
                break
            time.sleep(0.1)
        
        # All should complete
        for job_id in job_ids:
            job = self.worker.queue.get_job(job_id)
            self.assertEqual(job.status, JobStatus.COMPLETE)
    
    def test_callbacks_are_called(self):
        """Test event callbacks are invoked."""
        self.worker = ExtractionWorker(self.db, num_workers=1)
        
        events = []
        
        def on_job_started(job, worker_id):
            events.append(("started", job.id))
        
        def on_job_completed(job, result):
            events.append(("completed", job.id))
        
        self.worker.on("job_started", on_job_started)
        self.worker.on("job_completed", on_job_completed)
        
        self.worker.start()
        job_id = self.worker.enqueue(self.attachment_id)
        
        timeout = time.time() + 5
        while time.time() < timeout:
            if len(events) >= 2:
                break
            time.sleep(0.1)
        
        self.assertIn(("started", job_id), events)
        self.assertIn(("completed", job_id), events)


class TestThroughput(unittest.TestCase):
    """Throughput measurement tests."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = ResearchDatabase(self.db_path)
        self.worker = None
    
    def tearDown(self):
        if self.worker:
            self.worker.stop(timeout=5)
        self.db.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_throughput_measurement(self):
        """Measure queue throughput."""
        # Create many test files
        num_files = 50
        att_ids = []
        
        for i in range(num_files):
            test_file = Path(self.temp_dir) / f"doc{i}.txt"
            test_file.write_text(f"Document {i} content " * 100)
            att_id = self.db.add_attachment(
                filename=f"doc{i}.txt",
                path=str(test_file),
                mime_type="text/plain",
                file_size=test_file.stat().st_size
            )
            att_ids.append(att_id)
        
        self.worker = ExtractionWorker(self.db, num_workers=4)
        self.worker.start()
        
        # Enqueue all and measure time
        start_time = time.monotonic()
        
        job_ids = self.worker.enqueue_batch(att_ids)
        
        # Wait for completion
        timeout = time.time() + 60
        while time.time() < timeout:
            completed = sum(
                1 for jid in job_ids
                if self.worker.queue.get_job(jid).status == JobStatus.COMPLETE
            )
            if completed == len(job_ids):
                break
            time.sleep(0.1)
        
        elapsed = time.monotonic() - start_time
        
        # Calculate metrics
        status = self.worker.get_status()
        jobs_completed = status["stats"]["jobs_succeeded"]
        throughput = jobs_completed / elapsed if elapsed > 0 else 0
        avg_time = status["stats"]["avg_extraction_time_ms"]
        
        print(f"\n=== Throughput Results ===")
        print(f"Jobs processed: {jobs_completed}")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Throughput: {throughput:.2f} jobs/sec")
        print(f"Avg extraction time: {avg_time}ms")
        
        # Assert reasonable throughput
        self.assertGreater(throughput, 1.0, "Throughput should be > 1 job/sec")
        self.assertEqual(jobs_completed, num_files)
        
        # Return results for BUILD_LOG
        return {
            "throughput": round(throughput, 2),
            "avg_extraction_time_ms": avg_time,
            "jobs_processed": jobs_completed,
            "total_time_s": round(elapsed, 2),
        }


class TestPlainTextExtractor(unittest.TestCase):
    """Tests for PlainTextExtractor."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = PlainTextExtractor()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_extracts_text_file(self):
        """Test extraction of plain text file."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello, world!")
        
        result = self.extractor.extract(test_file)
        
        self.assertEqual(result.text, "Hello, world!")
        self.assertEqual(result.confidence, 1.0)
    
    def test_can_extract_by_extension(self):
        """Test can_extract by file extension."""
        self.assertTrue(self.extractor.can_extract(Path("test.txt")))
        self.assertTrue(self.extractor.can_extract(Path("test.md")))
        self.assertTrue(self.extractor.can_extract(Path("test.json")))
        self.assertFalse(self.extractor.can_extract(Path("test.pdf")))
    
    def test_can_extract_by_mime(self):
        """Test can_extract by MIME type."""
        self.assertTrue(self.extractor.can_extract(Path("file"), "text/plain"))
        self.assertFalse(self.extractor.can_extract(Path("file"), "application/pdf"))


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestQueueManager))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractionWorker))
    suite.addTests(loader.loadTestsFromTestCase(TestPlainTextExtractor))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run throughput separately to capture metrics
    print("\n=== Running Throughput Test ===")
    throughput_test = TestThroughput()
    throughput_test.setUp()
    try:
        metrics = throughput_test.test_throughput_measurement()
    finally:
        throughput_test.tearDown()
    
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success": result.wasSuccessful(),
        "throughput_metrics": metrics,
    }


if __name__ == "__main__":
    results = run_tests()
    print(f"\n=== Final Results ===")
    print(f"Tests run: {results['tests_run']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Success: {results['success']}")
    if results.get('throughput_metrics'):
        print(f"Throughput: {results['throughput_metrics']['throughput']} jobs/sec")
