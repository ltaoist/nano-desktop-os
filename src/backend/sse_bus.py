"""
Nano Desktop OS - SSE 事件总线
管理 SSE 客户端连接，支持向所有已连接客户端广播事件
"""

import asyncio
import json


class SSEBus:
    """管理 SSE 连接的消息总线"""

    def __init__(self):
        self._queues: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        """注册一个新的 SSE 客户端，返回其专属消息队列"""
        q: asyncio.Queue = asyncio.Queue()
        self._queues.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        """移除客户端队列"""
        try:
            self._queues.remove(q)
        except ValueError:
            pass

    def publish(self, event: str, data: dict):
        """向所有已连接的 SSE 客户端广播事件"""
        payload = json.dumps(data, ensure_ascii=False)
        message = f"event: {event}\ndata: {payload}\n\n"
        stale = []
        for q in self._queues:
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                stale.append(q)
        for q in stale:
            self.unsubscribe(q)


sse_bus = SSEBus()
