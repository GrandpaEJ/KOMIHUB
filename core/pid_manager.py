import os
import signal
import psutil
import time
from .logging import logger

class PIDManager:
    def __init__(self, pid_file: str = "data/bot.pid"):
        self.pid_file = pid_file
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.pid_file), exist_ok=True)

    def save_pid(self, pid: int = None):
        """Save current process PID to file"""
        if pid is None:
            pid = os.getpid()
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            logger.debug(f"Saved PID {pid} to {self.pid_file}")
        except Exception as e:
            logger.error(f"Failed to save PID: {e}")

    def get_pid(self) -> int:
        """Get saved PID from file"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
        except Exception as e:
            logger.error(f"Failed to read PID: {e}")
        return None

    def is_running(self, pid: int = None) -> bool:
        """Check if a process is running"""
        if pid is None:
            pid = self.get_pid()

        if pid is None:
            return False

        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def kill_process(self, pid: int = None, timeout: int = 5) -> bool:
        """Kill a process gracefully"""
        if pid is None:
            pid = self.get_pid()

        if pid is None:
            return False

        try:
            process = psutil.Process(pid)
            if process.is_running():
                # Try graceful termination first
                process.terminate()

                # Wait for process to terminate
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if not process.is_running():
                        logger.info(f"Process {pid} terminated gracefully")
                        return True
                    time.sleep(0.1)

                # Force kill if still running
                if process.is_running():
                    process.kill()
                    logger.warning(f"Force killed process {pid}")
                    return True

            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False

    def cleanup_old_instances(self) -> int:
        """Kill any old bot instances"""
        current_pid = os.getpid()
        killed_count = 0

        try:
            # Find all python processes running main.py
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python3' or proc.info['name'] == 'python':
                        cmdline = proc.info['cmdline']
                        if cmdline and len(cmdline) > 1 and 'main.py' in cmdline[-1] and proc.info['pid'] != current_pid:
                            logger.info(f"Killing old bot instance: PID {proc.info['pid']}")
                            self.kill_process(proc.info['pid'])
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        return killed_count

# Global PID manager instance
pid_manager = PIDManager()