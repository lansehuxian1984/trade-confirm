from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os, json, requests, datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析信号名
        if '?' in self.path:
            params = parse_qs(self.path.split('?', 1)[1])
            signal = params.get('signal', ['未知'])[0]
        else:
            signal = '未知'

        kv_url = os.environ.get('KV_REST_API_URL')
        kv_token = os.environ.get('KV_REST_API_TOKEN')

        if not kv_url or not kv_token:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('KV 环境变量未配置'.encode())
            return

        today = datetime.date.today().isoformat()
        key = f"{today}_{signal}"
        value = json.dumps({"confirmed": True, "time": str(datetime.datetime.now())})

        try:
            resp = requests.post(
                f"{kv_url}/set/{key}?token={kv_token}",
                data=value,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'请求失败: {e}'.encode())
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'✅ 已确认 {signal} 调仓，当天不再提醒。'.encode('utf-8'))
