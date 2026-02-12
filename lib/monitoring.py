"""
Monitoring and Health Check Module for OC-Memory
Track performance metrics and system health
"""

import logging
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """시스템 성능 모니터링"""

    def __init__(self):
        self.metrics = {
            'total_files': 0,
            'total_errors': 0,
            'total_processing_time': 0.0,
            'start_time': datetime.now(),
        }
        self.peak_memory = 0

    def record_file_processing(self, duration_ms: float, success: bool = True):
        """파일 처리 기록"""
        self.metrics['total_processing_time'] += duration_ms
        if success:
            self.metrics['total_files'] += 1
        else:
            self.metrics['total_errors'] += 1

    def get_avg_processing_time(self) -> float:
        """평균 처리 시간 반환 (ms)"""
        if self.metrics['total_files'] == 0:
            return 0
        return self.metrics['total_processing_time'] / self.metrics['total_files']

    def record_memory_usage(self):
        """메모리 사용량 기록"""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.peak_memory = max(self.peak_memory, memory_mb)
        except Exception as e:
            logger.error(f"Failed to record memory: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """모든 메트릭 반환"""
        uptime = (datetime.now() - self.metrics['start_time']).total_seconds()
        return {
            'total_files_processed': self.metrics['total_files'],
            'total_errors': self.metrics['total_errors'],
            'avg_processing_time_ms': self.get_avg_processing_time(),
            'peak_memory_mb': self.peak_memory,
            'uptime_seconds': uptime,
            'success_rate': (
                self.metrics['total_files'] /
                (self.metrics['total_files'] + self.metrics['total_errors']) * 100
                if (self.metrics['total_files'] + self.metrics['total_errors']) > 0
                else 0
            ),
        }

    def log_metrics(self):
        """메트릭 로깅"""
        metrics = self.get_metrics()
        logger.info(
            "Performance Metrics",
            extra={
                'files_processed': metrics['total_files_processed'],
                'errors': metrics['total_errors'],
                'avg_time_ms': f"{metrics['avg_processing_time_ms']:.2f}",
                'peak_memory_mb': f"{metrics['peak_memory_mb']:.2f}",
                'uptime_hours': f"{metrics['uptime_seconds'] / 3600:.2f}",
                'success_rate': f"{metrics['success_rate']:.1f}%",
            }
        )


class HealthChecker:
    """시스템 상태 확인"""

    def __init__(self, memory_dir: str, log_file: str = "oc-memory.log"):
        self.memory_dir = Path(memory_dir).expanduser()
        self.log_file = log_file

    def check_memory_directory(self) -> bool:
        """메모리 디렉토리 확인"""
        try:
            if not self.memory_dir.exists():
                logger.error(f"Memory directory not found: {self.memory_dir}")
                return False

            if not os.access(str(self.memory_dir), os.W_OK):
                logger.error(f"Memory directory not writable: {self.memory_dir}")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to check memory directory: {e}")
            return False

    def check_disk_space(self, min_gb: int = 1) -> bool:
        """디스크 공간 확인"""
        try:
            disk_usage = psutil.disk_usage(str(self.memory_dir))
            free_gb = disk_usage.free / 1024 / 1024 / 1024

            if free_gb < min_gb:
                logger.warning(f"Low disk space: {free_gb:.2f}GB free")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            return False

    def check_memory_usage(self, max_percent: float = 80.0) -> bool:
        """메모리 사용량 확인"""
        try:
            memory_percent = psutil.virtual_memory().percent

            if memory_percent > max_percent:
                logger.warning(f"High memory usage: {memory_percent:.1f}%")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to check memory usage: {e}")
            return False

    def check_log_file(self) -> bool:
        """로그 파일 확인"""
        try:
            log_path = Path(self.log_file)

            if log_path.exists():
                # 로그 파일 크기 확인 (100MB 초과 시 경고)
                size_mb = log_path.stat().st_size / 1024 / 1024
                if size_mb > 100:
                    logger.warning(f"Large log file: {size_mb:.1f}MB")

            return True
        except Exception as e:
            logger.error(f"Failed to check log file: {e}")
            return False

    def run_health_check(self) -> Dict[str, bool]:
        """전체 상태 확인"""
        checks = {
            'memory_directory': self.check_memory_directory(),
            'disk_space': self.check_disk_space(),
            'memory_usage': self.check_memory_usage(),
            'log_file': self.check_log_file(),
        }

        all_ok = all(checks.values())

        if all_ok:
            logger.info("Health check passed")
        else:
            logger.warning(
                "Health check failed",
                extra={'failed_checks': [k for k, v in checks.items() if not v]}
            )

        return checks


# 프로세스별 모니터링
import os


class ProcessMonitor:
    """프로세스 성능 모니터링"""

    @staticmethod
    def get_process_stats() -> Dict[str, Any]:
        """현재 프로세스 통계"""
        try:
            process = psutil.Process()
            return {
                'pid': process.pid,
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads(),
                'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
            }
        except Exception as e:
            logger.error(f"Failed to get process stats: {e}")
            return {}

    @staticmethod
    def log_process_stats():
        """프로세스 통계 로깅"""
        stats = ProcessMonitor.get_process_stats()
        if stats:
            logger.info(
                "Process Stats",
                extra=stats
            )


if __name__ == "__main__":
    # 테스트 코드
    logging.basicConfig(level=logging.INFO)

    # PerformanceMonitor 테스트
    monitor = PerformanceMonitor()
    monitor.record_file_processing(100.5, True)
    monitor.record_file_processing(50.3, True)
    monitor.record_memory_usage()
    monitor.log_metrics()

    # HealthChecker 테스트
    checker = HealthChecker("~/.openclaw/workspace/memory")
    checks = checker.run_health_check()
    print(f"Health checks: {checks}")

    # ProcessMonitor 테스트
    ProcessMonitor.log_process_stats()
