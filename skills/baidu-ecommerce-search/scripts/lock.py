#!/usr/bin/env python3
"""
跨进程文件锁 + QPS限流控制
用于实现 API 调用的频率限制
"""
import os
import time
import sys

# 锁文件路径（放在 scripts 目录下）
_script_dir = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(_script_dir, ".baidu_ec_lock")

# QPS控制配置
_min_request_interval = 1.0  # 默认最小请求间隔（秒），即1 QPS

# 从环境变量读取默认QPS
def _init_qps_from_env():
    """从环境变量初始化QPS"""
    global _min_request_interval
    qps_env = os.environ.get("BAIDU_EC_SEARCH_QPS")
    if qps_env:
        try:
            qps = float(qps_env)
            if qps > 0:
                _min_request_interval = 1.0 / qps
            else:
                _min_request_interval = 0
        except ValueError:
            pass  # 无效值，使用默认值

_init_qps_from_env()


def set_qps(qps):
    """
    设置最大QPS（每秒请求数）

    Args:
        qps: 每秒请求数，如 1 表示每秒最多1次请求，0.5 表示每2秒1次请求
    """
    global _min_request_interval
    if qps <= 0:
        _min_request_interval = 0
    else:
        _min_request_interval = 1.0 / qps


def _get_lock_file_path():
    """获取锁文件路径"""
    lock_dir = os.path.dirname(LOCK_FILE)
    if lock_dir and not os.path.exists(lock_dir):
        os.makedirs(lock_dir, exist_ok=True)
    return LOCK_FILE


def _acquire_lock(timeout=None):
    """
    获取文件锁

    Args:
        timeout: 超时时间（秒），None 表示无限等待

    Returns:
        文件描述符对象，失败返回 None
    """
    lock_file = _get_lock_file_path()
    start_time = time.time()

    while True:
        fd = None
        try:
            if sys.platform == "win32":
                # Windows 使用 msvcrt
                import msvcrt
                fd = open(lock_file, 'a+')
                try:
                    msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
                    return fd
                except IOError:
                    fd.close()
                    fd = None
            else:
                # Unix/macOS 使用 fcntl
                import fcntl
                fd = open(lock_file, 'a+')
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return fd
                except (IOError, BlockingIOError):
                    fd.close()
                    fd = None
        except (OSError, IOError):
            pass  # 文件操作失败，稍后重试

        # 检查超时
        if timeout is not None:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                return None

        # 等待后重试
        time.sleep(0.1)


def _release_lock(fd):
    """释放文件锁"""
    if fd is None:
        return

    try:
        try:
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            fd.close()
    except Exception:
        pass


def wait_for_rate_limit():
    """
    等待以满足QPS限制（跨进程同步）
    获取锁 → 读取上次请求时间 → 计算等待时间 → 睡眠 → 更新时间 → 释放锁
    """
    if _min_request_interval <= 0:
        return  # 无限制

    fd = _acquire_lock(timeout=60)  # 最多等待60秒
    if fd is None:
        return  # 获取锁超时，继续执行

    try:
        # 获取锁成功，读取上次请求时间
        try:
            fd.seek(0)
            content = fd.read().strip()
            if content:
                last_time = float(content)
            else:
                last_time = 0
        except (OSError, ValueError):
            last_time = 0  # 读取失败，使用0表示首次请求

        # 检查是否需要等待
        elapsed = time.time() - last_time
        if elapsed < _min_request_interval:
            time.sleep(_min_request_interval - elapsed)

        # 更新请求时间
        try:
            fd.seek(0)
            fd.truncate()
            fd.write(str(time.time()))
            fd.flush()
        except OSError:
            pass  # 写入失败，不影响本次请求
    finally:
        _release_lock(fd)


# ============ 以下为通用文件锁类 ============

class FileLock:
    """跨进程文件锁"""

    def __init__(self, lock_file=None):
        self.lock_file = lock_file or LOCK_FILE
        self.lock_fd = None
        self._platform = sys.platform

    def acquire(self, timeout=None):
        """
        获取锁

        Args:
            timeout: 超时时间（秒），None 表示无限等待

        Returns:
            True: 获取成功
            False: 超时
        """
        # 确保锁文件目录存在
        lock_dir = os.path.dirname(self.lock_file)
        if lock_dir and not os.path.exists(lock_dir):
            os.makedirs(lock_dir, exist_ok=True)

        start_time = time.time()

        while True:
            fd = None
            try:
                if self._platform == "win32":
                    import msvcrt
                    fd = open(self.lock_file, 'a+')
                    try:
                        msvcrt.locking(fd.fileno(), msvcrt.LK_NBLCK, 1)
                        self.lock_fd = fd
                        return True
                    except IOError:
                        fd.close()
                        self.lock_fd = None
                else:
                    import fcntl
                    fd = open(self.lock_file, 'a+')
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        self.lock_fd = fd
                        return True
                    except (IOError, BlockingIOError):
                        fd.close()
                        self.lock_fd = None
            except (OSError, IOError):
                pass

            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False

            time.sleep(0.1)

    def release(self):
        """释放锁"""
        if self.lock_fd is not None:
            try:
                if self._platform == "win32":
                    import msvcrt
                    msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            finally:
                try:
                    self.lock_fd.close()
                except OSError:
                    pass
                self.lock_fd = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def acquire_lock(timeout=None):
    """
    获取锁的便捷函数

    Args:
        timeout: 超时时间（秒）

    Returns:
        FileLock 对象
    """
    lock = FileLock()
    if not lock.acquire(timeout):
        raise RuntimeError(f"获取锁超时（{timeout}秒）")
    return lock


if __name__ == "__main__":
    # 测试锁功能
    lock = FileLock()
    print("尝试获取锁...")
    if lock.acquire():
        print("锁获取成功！按Enter键释放...")
        input()
        lock.release()
        print("锁已释放")
    else:
        print("获取锁失败")
