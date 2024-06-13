"""
Calculate tickets lucky numbers for certain ranges.

Example:
    124 223 -> lucky number cause 1+2+4 == 2+2+3
    101 203 -> not lucky number cause 1+0+1 != 2+0+3

"""
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


class Benchmark:
    """Context manager to measure execution time."""

    def __init__(self, name):
        """Init."""
        self.name = name
        self.start = None

    def __enter__(self):
        """Enter context manager."""
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit content manager."""
        duration = time.perf_counter() - self.start
        print(f'"{self.name}" run took {duration:.3f} sec')


class LuckyNumbersChecker:
    """Calculate lucky numbers with different approaches."""

    def __init__(self, max_ticket_num=999999, max_workers=4):
        """Init."""
        self.max_ticket_num = max_ticket_num
        self.max_workers = max_workers

        # pre-calculated additional values
        self.half_measure = 10 ** int(len(str(max_ticket_num)) / 2)  # for 999_999 -> 1000  9999_9999 -> 10000
        range_delta = int((max_ticket_num + 1) / max_workers)
        self.workers_ranges = [range(i * range_delta + 1, (i + 1) * range_delta + 1) for i in range(max_workers)]

    @staticmethod
    def sum_of_digits(num):
        """Digits sum."""
        d_sum = 0
        while num > 0:
            d_sum += num % 10
            num //= 10
        return d_sum

    def check_if_lucky(self, num):
        """Check if certain number lucky."""
        left = num // self.half_measure
        right = num % self.half_measure
        if left and right:
            return self.sum_of_digits(left) == self.sum_of_digits(right)
        return False

    def check_range(self, range_val):
        """Check certain range for lucky numbers."""
        return sum(self.check_if_lucky(curr_num) for curr_num in range_val)

    def raw_check(self):
        """No threads and multiprocesses."""
        with Benchmark('Raw'):
            return self.check_range(range(1, self.max_ticket_num + 1))

    def thread_pool_check(self):
        """Threads usage."""
        with Benchmark('ThreadPoolExecutor'):
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                results = executor.map(self.check_range, self.workers_ranges)
                return sum(results)

    def process_pool_check(self):
        """Multiprocessing."""
        with Benchmark('ProcessPoolExecutor'):
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                results = executor.map(self.check_range, self.workers_ranges)
                return sum(results)


if __name__ == '__main__':
    lucky_checker = LuckyNumbersChecker(max_ticket_num=9999_9999, max_workers=5)
    print(lucky_checker.raw_check())
    print(lucky_checker.thread_pool_check())
    print(lucky_checker.process_pool_check())
