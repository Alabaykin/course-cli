from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def generate_xapi_statement(
    verb_id: str,
    verb_display: str,
    course_title: str,
    course_path: str,
    success: bool = True,
    extensions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    '''
    Generate an xAPI statement for a course action.

    Args:
        verb_id (str): xAPI verb identifier URI.
        verb_display (str): Russian display name for the verb.
        course_title (str): Title of the course.
        course_path (str): Path to the course.
        success (bool): Whether the action succeeded.
        extensions (dict): Additional statement extensions.

    Returns:
        dict[str, Any]: Formatted xAPI statement dictionary.
    '''
    load_env()
    
    teacher_name = os.environ.get('TEACHER_NAME', 'Преподаватель')
    teacher_email = os.environ.get('TEACHER_EMAIL', 'teacher@example.com')
    
    mbox = teacher_email
    if not mbox.startswith('mailto:'):
        mbox = f'mailto:{mbox}'

    course_abs_path = str(Path(course_path).resolve())
    course_id_safe = course_title.lower().replace(' ', '-')
    object_id = f'https://example.edu/courses/{course_id_safe}'
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    statement = {
        'actor': {
            'name': teacher_name,
            'mbox': mbox,
            'objectType': 'Agent'
        },
        'verb': {
            'id': verb_id,
            'display': {
                'ru-RU': verb_display,
                'en-US': verb_display
            }
        },
        'object': {
            'id': object_id,
            'definition': {
                'name': {
                    'ru-RU': course_title
                },
                'type': 'http://adlnet.gov/expapi/activities/course',
                'extensions': {
                    'https://example.edu/xapi/extensions/course-path': course_abs_path
                }
            },
            'objectType': 'Activity'
        },
        'result': {
            'success': success,
        },
        'timestamp': timestamp
    }

    if extensions:
        statement['result']['extensions'] = extensions

    return statement


def send_xapi_statement(statement: dict[str, Any]) -> None:
    '''
    Send xAPI statement to LRS (if configured) and write to local mock_lrs.log.

    Args:
        statement (dict[str, Any]): The xAPI statement to send.
    '''
    # 1. Запись в локальный лог mock_lrs.log
    log_path = Path('mock_lrs.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(statement, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f'Ошибка записи в локальный LRS лог: {e}', file=sys.stderr)

    # 2. Отправка во внешний LRS
    load_env()
    lrs_url = os.environ.get('LRS_URL')
    mock_mode = os.environ.get('LRS_MOCK_MODE', 'True').lower() == 'true'

    if lrs_url and not mock_mode:
        import urllib.request
        from urllib.error import URLError
        
        try:
            data = json.dumps(statement, ensure_ascii=False).encode('utf-8')
            req = urllib.request.Request(
                lrs_url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'X-Experience-API-Version': '1.0.3'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                pass
        except URLError as e:
            print(f'Предупреждение: не удалось отправить xAPI событие в LRS: {e}', file=sys.stderr)
        except Exception as e:
            print(f'Предупреждение: ошибка при отправке xAPI события: {e}', file=sys.stderr)


