import json
import urllib.request
import urllib.error

base_url = 'http://127.0.0.1:8000'

payload_enroll = {
    'user_id': 'test_user_123',
    'username': 'Test User',
    'email': 'test@example.com',
    'keystroke_samples': [
        [
            {
                'key': 'a',
                'dwellTime': 100,
                'flightTime': 120,
                'latency': 30,
                'holdTime': 100,
                'timestamp': 1.0,
            }
        ]
    ],
}

req = urllib.request.Request(
    f'{base_url}/auth/enroll',
    data=json.dumps(payload_enroll).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)

try:
    with urllib.request.urlopen(req) as resp:
        print('ENROLL STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('ENROLL ERROR', e.code)
    print(e.read().decode('utf-8'))

payload_auth = {
    'user_id': 'test_user_123',
    'keystrokes': [
        {
            'key': 'a',
            'dwellTime': 100,
            'flightTime': 120,
            'latency': 30,
            'holdTime': 100,
            'timestamp': 1.0,
        }
    ],
    'session_id': 'session-1',
}

req2 = urllib.request.Request(
    f'{base_url}/auth/authenticate',
    data=json.dumps(payload_auth).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)

try:
    with urllib.request.urlopen(req2) as resp2:
        print('AUTH STATUS', resp2.status)
        print(resp2.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('AUTH ERROR', e.code)
    print(e.read().decode('utf-8'))
