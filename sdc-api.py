import asyncio, aiohttp, json
from aiohttp import ClientSession
from datetime import datetime, timedelta


class Guild:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "New Guild")
        self.id = kwargs.get("id", "")
        self.description = kwargs.get("des", kwargs.get("description", ""))
        self.invite = kwargs.get("invite")
        self.online = kwargs.get("online", 0)
        self.members = kwargs.get("members", 0)
        self.ups = kwargs.get("upCount", 0)
        self._api = kwargs.get("api", SDC())

    async def place(self):
        return await self._api.get_place(self.id)


    def __str__(self):
        return "<Guild: {0.name}, ID: {0.id}, Description: {0.description}, Invite: {0.invite}, Members: {0.online}/{0.members}, UPs: {0.ups}>".format(self)

    def __repr__(self):
        return "<Guild: {0.name}, ID: {0.id}, Description: {0.description}, Invite: {0.invite}, Members: {0.online}/{0.members}, UPs: {0.ups}>".format(self)


class SDC:
    def __init__(self, *args, **kwargs):
        self.token = kwargs.get("token")
        self.last_request = datetime.utcnow()-timedelta(seconds=3)
        self.route = "https://api.server-discord.com"

    def req_cd(func):
        async def check_time(*args, **kwargs):
            now = datetime.utcnow().timestamp()
            next = (args[0].last_request + timedelta(seconds=3)).timestamp()
            if now < next:
                await asyncio.sleep(next-now)
            return await func(*args, **kwargs)
        return check_time

    @req_cd
    async def _request(self, method, type, **kwargs):
        id = "/"+str(kwargs.get("id")) if kwargs.get("id") else ""
        special = "/"+str(kwargs.get("special")) if kwargs.get("special") else ""
        url = "{route}/{type}{id}{special}".format(
            route=self.route,
            type=type,
            id=id,
            special=special
        )
        params = {
            "dKey": self.token
        }
        self.last_request = datetime.utcnow()

        async with ClientSession() as session:
            methods = {
                "get": session.get,
                "post": session.post,
                "put": session.put,
                "patch": session.patch,
                "delete": session.delete
            }
            method = methods.get(method.lower(), session.get)

            async with method(url, params=params) as response:
                if response.status == 200:
                    resp = await response.json()
                    error = resp.get("error")
                    if error:
                        print("Error '{type}': {text}".format(
                            type=error.get("type", "Unknown"),
                            text=error.get("message", "Unknown")
                        ))
                    return resp
                elif response.status == 401:
                    raise Exception("Unauthorized")
                else:
                    return None

    async def get_guild(self, id=None):
        resp = await self._request("get", "guild", id=id)
        resp["id"] = id
        resp["api"] = self
        return Guild(**resp)

    async def get_place(self, id=None):
        resp = await self._request("get", "guild", id=id, special="place")
        return resp.get("place", -1)