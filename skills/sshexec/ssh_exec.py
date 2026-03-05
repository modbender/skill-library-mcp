"""Execute SSH commands with password or key authentication.

This script is intended to be used as a skill entry point. It connects to a
remote host over SSH, runs a single command, and prints the stdout/stderr
along with an appropriate exit code.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Optional

try:
	import paramiko
except ImportError as exc:  # pragma: no cover - dependency check
	sys.stderr.write(
		"Missing dependency 'paramiko'. Install with `pip install paramiko` before running.\n"
	)
	raise SystemExit(1) from exc


LOG = logging.getLogger("ssh_exec")


def configure_logging(verbose: bool) -> None:
	level = logging.DEBUG if verbose else logging.INFO
	logging.basicConfig(
		level=level,
		format="%(asctime)s %(levelname)s %(name)s: %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)


def load_private_key(key_path: str, passphrase: Optional[str]) -> paramiko.PKey:
	"""Load a private key, trying common key types until one succeeds."""

	loaders = (
		paramiko.RSAKey.from_private_key_file,
		paramiko.ECDSAKey.from_private_key_file,
		paramiko.Ed25519Key.from_private_key_file,
	)

	for loader in loaders:
		try:
			return loader(key_path, password=passphrase)
		except paramiko.PasswordRequiredException:
			raise
		except paramiko.SSHException:
			continue

	raise ValueError(f"Unable to read private key at {key_path}")


def run_command(
	host: str,
	user: str,
	command: str,
	*,
	port: int = 22,
	password: Optional[str] = None,
	key_path: Optional[str] = None,
	key_passphrase: Optional[str] = None,
	timeout: int = 30,
	strict_host_key: bool = False,
	pty: bool = False,
) -> int:
	"""Connect and execute a single command, returning the remote exit status."""

	client = paramiko.SSHClient()
	if strict_host_key:
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.RejectPolicy())
	else:
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	pkey = None
	if key_path:
		if not os.path.exists(key_path):
			raise FileNotFoundError(f"Private key not found: {key_path}")
		pkey = load_private_key(key_path, key_passphrase)

	LOG.debug("Connecting to %s:%s as %s", host, port, user)

	try:
		client.connect(
			hostname=host,
			port=port,
			username=user,
			password=password,
			pkey=pkey,
			look_for_keys=False,
			allow_agent=True,
			timeout=timeout,
		)
	except Exception:
		LOG.exception("SSH connection failed")
		raise

	try:
		LOG.info("Executing command: %s", command)
		stdin, stdout, stderr = client.exec_command(command, timeout=timeout, get_pty=pty)
		exit_code = stdout.channel.recv_exit_status()

		out_text = stdout.read().decode(errors="replace")
		err_text = stderr.read().decode(errors="replace")

		if out_text:
			LOG.info("Command stdout:\n%s", out_text.rstrip())
		if err_text:
			LOG.warning("Command stderr:\n%s", err_text.rstrip())

		LOG.info("Command completed with exit code %s", exit_code)
		return exit_code
	finally:
		client.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Execute a remote SSH command")
	parser.add_argument("--host", required=True, help="Target host or IP")
	parser.add_argument("--user", required=True, help="SSH username")
	parser.add_argument("--command", required=True, help="Command to execute remotely")
	parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
	parser.add_argument("--password", help="Password for authentication")
	parser.add_argument("--key", dest="key_path", help="Path to private key file")
	parser.add_argument("--key-passphrase", dest="key_passphrase", help="Passphrase for the private key, if needed")
	parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds for connect/exec (default: 30)")
	parser.add_argument(
		"--strict-host-key",
		action="store_true",
		help="Require known_hosts entry and refuse unknown hosts",
	)
	parser.add_argument("--pty", action="store_true", help="Request a pseudo-tty for the remote command (useful for sudo)")
	parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
	return parser.parse_args(argv)


def main(argv: list[str]) -> int:
	args = parse_args(argv)
	configure_logging(args.verbose)

	if not args.password and not args.key_path:
		LOG.error("Either --password or --key must be provided for authentication")
		return 2

	try:
		return run_command(
			host=args.host,
			user=args.user,
			command=args.command,
			port=args.port,
			password=args.password,
			key_path=args.key_path,
			key_passphrase=args.key_passphrase,
			timeout=args.timeout,
			strict_host_key=args.strict_host_key,
			pty=args.pty,
		)
	except FileNotFoundError as exc:
		LOG.error(str(exc))
		return 3
	except paramiko.AuthenticationException:
		LOG.error("Authentication failed for user %s", args.user)
		return 4
	except paramiko.SSHException as exc:
		LOG.error("SSH error: %s", exc)
		return 5
	except Exception as exc:  # pragma: no cover - catch-all for clarity
		LOG.exception("Unexpected error: %s", exc)
		return 6


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
