# examples/server_simple.py
from typing import List

import sqlalchemy
from aiohttp import web, web_routedef

import src.filter
from src.filter import Filter


async def handle(request):
    name = request.match_info.get("nam", "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)


async def wshandle(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            await ws.send_str("Hello, {}".format(msg.data))
        elif msg.type == web.WSMsgType.binary:
            await ws.send_bytes(msg.data)
        elif msg.type == web.WSMsgType.close:
            break

    return ws


app = web.Application()
route = web.RouteTableDef()


@route.get("/")
async def hello(request):
    return web.Response(text="Hello world")


app.add_routes(route)
app.add_routes([web.get("/echo", wshandle), web.get("/{nam}", handle)])


# web.run_app(app)

nums = [1, 1, 2, 1]
target = 3


class Scraper(Filter):
    def __init__(self, id: int) -> None:
        super().__init__(id)


class Solution:
    def __init__(self) -> None:
        self.dp = {}

    def thing(self, nums: List[int], target: int) -> int:
        n = len(nums)

        def dfs(i, total):
            if i == n:
                if total == target:
                    return 1
                else:
                    return 0

            if (i, total) in self.dp:
                return self.dp[(i, total)]
            self.dp[(i, total)] = dfs(i + 1, total + nums[i]) + dfs(
                i + 1, total - nums[i]
            )
            return self.dp[(i, total)]

        return dfs(0, 0)


m = Solution()
print(m.thing(nums=nums, target=target))
print(m.dp)
