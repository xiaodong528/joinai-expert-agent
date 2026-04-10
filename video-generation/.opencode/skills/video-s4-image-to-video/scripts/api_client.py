"""
统一 HTTP 客户端 — AI 视频生成管线公共模块

支持:
- 火山引擎 (ARK_API_KEY, Bearer token)
- MiniMax (MINIMAX_API_KEY, Bearer token)
- 快手可灵 (KLING_ACCESS_KEY + KLING_SECRET_KEY, JWT 签名)
- 阿里云百炼 (DASHSCOPE_API_KEY, Bearer token)

用法:
    client = APIClient("ark")
    resp = client.post("/images/generations", json={...})
"""

import hashlib
import hmac
import json
import os
import time
from urllib.parse import urljoin

import requests


class APIClient:
    """统一 HTTP 客户端，封装认证、重试、超时逻辑。"""

    PLATFORMS = {
        "ark": {
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "env_key": "ARK_API_KEY",
            "auth_type": "bearer",
        },
        "minimax": {
            "base_url": "https://api.minimaxi.com/v1",
            "env_key": "MINIMAX_API_KEY",
            "auth_type": "bearer",
        },
        "kling": {
            "base_url": "https://api.klingai.com/v1",
            "env_keys": ("KLING_ACCESS_KEY", "KLING_SECRET_KEY"),
            "auth_type": "jwt",
        },
        "dashscope": {
            "base_url": "https://dashscope.aliyuncs.com/api/v1",
            "env_key": "DASHSCOPE_API_KEY",
            "auth_type": "bearer",
        },
    }

    def __init__(self, platform: str, max_retries: int = 3, timeout: int = 30):
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unknown platform: {platform}. Supported: {list(self.PLATFORMS.keys())}")

        self.config = self.PLATFORMS[platform]
        self.platform = platform
        self.base_url = self.config["base_url"]
        self.max_retries = max_retries
        self.timeout = timeout
        self._session = requests.Session()
        self._load_credentials()

    def _load_credentials(self):
        """从环境变量加载认证凭据。"""
        if self.config["auth_type"] == "jwt":
            keys = self.config["env_keys"]
            self.access_key = os.environ.get(keys[0])
            self.secret_key = os.environ.get(keys[1])
            if not self.access_key or not self.secret_key:
                raise EnvironmentError(
                    f"Missing env vars: {keys[0]} and/or {keys[1]}"
                )
        else:
            env_key = self.config["env_key"]
            self.api_key = os.environ.get(env_key)
            if not self.api_key:
                raise EnvironmentError(f"Missing env var: {env_key}")

    def _get_headers(self) -> dict:
        """生成请求头，包含认证信息。"""
        headers = {"Content-Type": "application/json"}

        if self.config["auth_type"] == "bearer":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.config["auth_type"] == "jwt":
            token = self._generate_jwt()
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _generate_jwt(self) -> str:
        """为可灵 API 生成 JWT token（HS256 签名）。"""
        import base64

        now = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": now + 1800,  # 30 分钟有效期
            "nbf": now - 5,
        }

        def b64url(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

        header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.secret_key.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        signature_b64 = b64url(signature)

        return f"{signing_input}.{signature_b64}"

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """发送 HTTP 请求，带自动重试。"""
        url = f"{self.base_url}{path}" if path.startswith("/") else path
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("headers", {})
        kwargs["headers"].update(self._get_headers())

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.request(method, url, **kwargs)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 5))
                    print(f"  Rate limited, waiting {retry_after}s (attempt {attempt}/{self.max_retries})")
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                last_error = e
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    print(f"  Request failed: {e}, retrying in {wait}s (attempt {attempt}/{self.max_retries})")
                    time.sleep(wait)

        raise RuntimeError(
            f"Request failed after {self.max_retries} retries: {last_error}"
        )

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def download(self, url: str, dest_path: str) -> str:
        """下载文件到本地路径。"""
        resp = self._session.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest_path


if __name__ == "__main__":
    # 快速验证各平台认证
    for platform in ["ark", "minimax", "kling", "dashscope"]:
        try:
            client = APIClient(platform)
            print(f"{platform}: credentials loaded OK")
        except EnvironmentError as e:
            print(f"{platform}: {e}")
