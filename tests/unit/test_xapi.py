import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from course_cli.xapi import generate_xapi_statement, send_xapi_statement

def test_generate_xapi_statement():
    """
    Проверяет корректность формирования словаря xAPI: 
    структуры actor, verb, object, result и extensions.
    """
    os.environ['TEACHER_NAME'] = 'Test Teacher'
    os.environ['TEACHER_EMAIL'] = 'test@example.com'
    
    stmt = generate_xapi_statement(
        verb_id='http://test/verb',
        verb_display='tested',
        course_title='xAPI Course',
        course_path='/tmp/course',
        success=True,
        extensions={'test-ext': 123}
    )
    
    assert stmt['actor']['name'] == 'Test Teacher'
    assert stmt['actor']['mbox'] == 'mailto:test@example.com'
    assert stmt['verb']['id'] == 'http://test/verb'
    assert stmt['result']['success'] is True
    assert stmt['result']['extensions']['test-ext'] == 123
    assert 'xapi-course' in stmt['object']['id']

