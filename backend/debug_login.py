import urllib.request
import urllib.error
import json

base = 'http://127.0.0.1:8000'
newuser = 'login_test_123'

payload = {
    'user_id': newuser,
    'username': 'Login Test',
    'email': 'login@test.com',
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
    f'{base}/auth/enroll',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)

try:
    with urllib.request.urlopen(req) as r:
        print('ENROLL', r.status)
        print(r.read().decode())
except urllib.error.HTTPError as e:
    print('ENROLL ERR', e.code)
    print(e.read().decode())

payload2 = {
    'user_id': newuser,
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
    'session_id': 'session-login-test',
}

req2 = urllib.request.Request(
    f'{base}/auth/authenticate',
    data=json.dumps(payload2).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)

try:
    with urllib.request.urlopen(req2) as r2:
        print('AUTH', r2.status)
        print(r2.read().decode())
except urllib.error.HTTPError as e:
    print('AUTH ERR', e.code)
    print(e.read().decode())
except Exception as e:
    print('AUTH EXC', type(e).__name__, e)
