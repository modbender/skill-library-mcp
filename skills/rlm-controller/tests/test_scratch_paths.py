#!/usr/bin/env python3
"""Tests that rlm_auto.py stores temporary files only under expected workspace scratch paths
and that subcall prompts have secrets redacted by default."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')


class TestAutoScratchPaths(unittest.TestCase):
    """Verify rlm_auto.py output structure and redaction behavior."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Create a non-sensitive sample context file with an embedded fake secret
        self.ctx_file = os.path.join(self.tmpdir, 'sample_ctx.txt')
        sample_text = (
            "This is a sample document about widgets.\n"
            "The widget API is versioned.\n"
            "password = 'do-not-leak-this'\n"
            "More content about widgets and versioning.\n"
        ) * 20  # repeat to exceed keyword-hit threshold and produce multiple slices
        with open(self.ctx_file, 'w') as f:
            f.write(sample_text)
        self.outdir = os.path.join(self.tmpdir, 'run_output')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_auto(self, extra_args=None):
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_auto.py'),
            '--ctx', self.ctx_file,
            '--goal', 'summarize widget versioning',
            '--outdir', self.outdir,
        ]
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.tmpdir)
        self.assertEqual(result.returncode, 0, f"rlm_auto.py failed: {result.stderr}")
        return json.loads(result.stdout)

    # ------------------------------------------------------------------
    # Output structure
    # ------------------------------------------------------------------
    def test_plan_json_created(self):
        """plan.json should be created under outdir."""
        self._run_auto()
        self.assertTrue(os.path.isfile(os.path.join(self.outdir, 'plan.json')))

    def test_subcall_prompts_under_outdir(self):
        """All subcall prompt files must reside under outdir/subcalls/."""
        plan = self._run_auto()
        subcalls_dir = os.path.join(self.outdir, 'subcalls')
        for prompt in plan.get('subcall_prompts', []):
            path = prompt['file']
            real = os.path.realpath(path)
            self.assertTrue(
                real.startswith(os.path.realpath(subcalls_dir)),
                f"Prompt file {path} is outside expected subcalls dir",
            )
            self.assertTrue(os.path.isfile(path), f"Prompt file missing: {path}")

    def test_no_files_outside_outdir(self):
        """rlm_auto.py must not create files outside outdir (except the ctx file we provided)."""
        before = set()
        for root, dirs, files in os.walk(self.tmpdir):
            for fname in files:
                before.add(os.path.join(root, fname))

        self._run_auto()

        after = set()
        for root, dirs, files in os.walk(self.tmpdir):
            for fname in files:
                after.add(os.path.join(root, fname))

        new_files = after - before
        for nf in new_files:
            self.assertTrue(
                os.path.realpath(nf).startswith(os.path.realpath(self.outdir)),
                f"Unexpected file created outside outdir: {nf}",
            )

    # ------------------------------------------------------------------
    # Redaction (default: enabled)
    # ------------------------------------------------------------------
    def test_secrets_redacted_by_default(self):
        """With default settings, secrets in slice text should be redacted."""
        self._run_auto()
        subcalls_dir = os.path.join(self.outdir, 'subcalls')
        for fname in os.listdir(subcalls_dir):
            with open(os.path.join(subcalls_dir, fname), 'r') as f:
                content = f.read()
            self.assertNotIn('do-not-leak-this', content,
                             f"Secret leaked in {fname}")

    def test_secrets_present_when_redaction_disabled(self):
        """With --no-redact, secrets should remain in subcall prompts."""
        self._run_auto(extra_args=['--no-redact'])
        subcalls_dir = os.path.join(self.outdir, 'subcalls')
        found = False
        for fname in os.listdir(subcalls_dir):
            with open(os.path.join(subcalls_dir, fname), 'r') as f:
                content = f.read()
            if 'do-not-leak-this' in content:
                found = True
        self.assertTrue(found, "Expected secret to remain when --no-redact is used")

    def test_goal_secrets_redacted_by_default(self):
        """Secrets embedded in the goal text should also be redacted in subcall prompts."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_auto.py'),
            '--ctx', self.ctx_file,
            '--goal', 'find files with password=hunter2 in config',
            '--outdir', self.outdir,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.tmpdir)
        self.assertEqual(result.returncode, 0, f"rlm_auto.py failed: {result.stderr}")
        subcalls_dir = os.path.join(self.outdir, 'subcalls')
        for fname in os.listdir(subcalls_dir):
            with open(os.path.join(subcalls_dir, fname), 'r') as f:
                content = f.read()
            self.assertNotIn('hunter2', content,
                             f"Goal secret leaked in {fname}")


if __name__ == '__main__':
    unittest.main()
