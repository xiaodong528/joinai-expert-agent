"""
统一异步任务轮询器 — AI 视频生成管线公共模块

用于 Stage 4 (Seedance), Stage 6 (MiniMax Music), Stage 8 (可灵 Lip-Sync)
的 submit → poll → download 异步模式。

用法:
    from common.async_poller import poll_task

    result = poll_task(
        client=api_client,
        poll_url="/tasks/abc123",
        status_field="status",
        completed_value="completed",
        failed_value="failed",
        interval=5,
        timeout=300,
    )
"""

import time
from typing import Any

from api_client import APIClient


def poll_task(
    client: APIClient,
    poll_url: str,
    status_field: str = "status",
    completed_value: str = "completed",
    failed_value: str = "failed",
    result_field: str | None = None,
    interval: int = 5,
    timeout: int = 300,
    verbose: bool = True,
) -> dict[str, Any]:
    """
    轮询异步任务直到完成或超时。

    Args:
        client: APIClient 实例
        poll_url: 轮询端点路径（如 /tasks/{task_id}）
        status_field: 响应 JSON 中状态字段名
        completed_value: 完成状态值
        failed_value: 失败状态值
        result_field: 结果字段名（None 则返回整个响应）
        interval: 轮询间隔（秒）
        timeout: 超时时间（秒）
        verbose: 是否打印轮询进度

    Returns:
        任务结果 dict

    Raises:
        RuntimeError: 任务失败
        TimeoutError: 超时
    """
    elapsed = 0
    while elapsed < timeout:
        resp = client.get(poll_url)
        data = resp.json()

        # 处理嵌套 JSON 结构（有些 API 把状态放在 data.status）
        status_data = data
        for key in status_field.split("."):
            status_data = status_data.get(key, {}) if isinstance(status_data, dict) else {}
        status = status_data if isinstance(status_data, str) else data.get(status_field, "unknown")

        if verbose:
            print(f"  [{elapsed}s/{timeout}s] status: {status}")

        if status == completed_value:
            if result_field:
                result = data
                for key in result_field.split("."):
                    result = result.get(key, {})
                return result
            return data

        if status == failed_value:
            error_msg = data.get("error", data.get("message", "Unknown error"))
            raise RuntimeError(f"Task failed: {error_msg}\nFull response: {data}")

        time.sleep(interval)
        elapsed += interval

    raise TimeoutError(f"Task timed out after {timeout}s. Last status: {status}")


# 预配置的轮询参数
POLL_CONFIGS = {
    "seedance": {
        "status_field": "status",
        "completed_value": "completed",
        "failed_value": "failed",
        "interval": 5,
        "timeout": 300,
    },
    "minimax_music": {
        "status_field": "status",
        "completed_value": "Success",
        "failed_value": "Failed",
        "interval": 5,
        "timeout": 300,
    },
    "kling_lipsync": {
        "status_field": "data.task_status",
        "completed_value": "succeed",
        "failed_value": "failed",
        "interval": 5,
        "timeout": 600,
    },
}


def poll_with_config(
    client: APIClient,
    poll_url: str,
    config_name: str,
    result_field: str | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """使用预配置参数轮询。"""
    if config_name not in POLL_CONFIGS:
        raise ValueError(f"Unknown config: {config_name}. Supported: {list(POLL_CONFIGS.keys())}")

    config = POLL_CONFIGS[config_name]
    return poll_task(
        client=client,
        poll_url=poll_url,
        result_field=result_field,
        verbose=verbose,
        **config,
    )
