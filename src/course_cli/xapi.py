from __future__ import annotations

import os
import sys
from pathlib import Path


def load_env(env_path: str | Path = '.env') -> None:
    '''
    Load environment variables from a .env file.

    Args:
        env_path (str | Path): Path to the .env file.
    '''
    path = Path(env_path)
    if not path.exists():
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    key_str = key.strip()
                    val_str = val.strip().strip('\'"')
                    os.environ[key_str] = val_str
    except Exception as e:
        print(f'Ошибка при чтении .env: {e}', file=sys.stderr)
