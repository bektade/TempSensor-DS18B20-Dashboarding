import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

TRANSFORM_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TRANSFORM_DIR.parent.parent
COALESCE_SCRIPT = TRANSFORM_DIR / 'coalesce_sensor_data.py'
DEFAULT_INTERVAL_SEC = 30


def run_coalesce() -> int:
    result = subprocess.run(
        [sys.executable, str(COALESCE_SCRIPT)],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Run coalesce_sensor_data.py on a fixed interval.'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=DEFAULT_INTERVAL_SEC,
        help='Seconds between coalesce runs (default: 30)',
    )
    args = parser.parse_args()

    print(
        f'Coalesce scheduler: every {args.interval}s '
        f'({COALESCE_SCRIPT.relative_to(PROJECT_ROOT)})'
    )
    print('Press Ctrl+C to stop.\n')

    try:
        while True:
            started = datetime.now().isoformat(sep=' ', timespec='seconds')
            print(f'[{started}] Running coalesce...')
            exit_code = run_coalesce()
            if exit_code != 0:
                print(f'[{started}] Coalesce finished with exit code {exit_code}')
            print()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nCoalesce scheduler stopped.')


if __name__ == '__main__':
    main()
