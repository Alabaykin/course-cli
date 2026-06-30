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

@patch('urllib.request.urlopen')
def test_send_xapi_statement_http(mock_urlopen, tmp_path: Path, monkeypatch):
    """
    Проверяет отправку HTTP POST запроса во внешний LRS, 
    если MOCK_MODE отключен, и запись события в локальный лог.
    """
    monkeypatch.chdir(tmp_path)
    
    os.environ['LRS_URL'] = 'http://lrs.example.com/data/xAPI/statements'
    os.environ['LRS_MOCK_MODE'] = 'false'
    
    stmt = {'test': 'data'}
    send_xapi_statement(stmt)
    
    # Проверяем вызов POST запроса
    mock_urlopen.assert_called_once()
    
    # Проверяем запись в локальный лог
    log_path = tmp_path / 'mock_lrs.log'
    assert log_path.exists()
    assert '{"test": "data"}' in log_path.read_text(encoding='utf-8')

def test_send_xapi_statement_mock_mode(tmp_path: Path, monkeypatch):
    """
    Проверяет, что в режиме MOCK_MODE сетевой запрос НЕ отправляется, 
    но локальная запись лога по-прежнему происходит.
    """
    monkeypatch.chdir(tmp_path)
    
    os.environ['LRS_URL'] = 'http://lrs.example.com/data/xAPI/statements'
    os.environ['LRS_MOCK_MODE'] = 'true'
    
    stmt = {'mock': 'mode'}
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        send_xapi_statement(stmt)
        # Убеждаемся, что HTTP запрос заглушен
        mock_urlopen.assert_not_called()
        
    # Локальный лог должен быть записан
    log_path = tmp_path / 'mock_lrs.log'
    assert log_path.exists()
