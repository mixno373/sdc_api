import asyncio, aiohttp, json
from aiohttp import ClientSession
from datetime import datetime, timedelta



class Vote:
    def __init__(self, *args, **kwargs):
        self.guild = kwargs.get("guild", Guild())
        self.user = kwargs.get("user", User(id=kwargs.get("id")))
        self.count = kwargs.get("count", 0)

        if not isinstance(self.guild, Guild):
            self.guild = Guild(id=kwargs.get("guild"))
        if not isinstance(self.user, User):
            self.user = User(id=kwargs.get("user"))

        self._api = kwargs.get("api", SDC())


    def __str__(self):
        return "<Vote | Guild: {0.guild.name}, User: {0.user.name}#{0.user.discriminator}, ID: {0.user.id}, count: {0.count}>".format(self)

    def __repr__(self):
        return "<Vote | Guild: {0.guild.name}, User: {0.user.name}#{0.user.discriminator}, ID: {0.user.id}, count: {0.count}>".format(self)


class User:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "Deleted User")
        self.discriminator = kwargs.get("discriminator", "0000")
        self.id = kwargs.get("id", "")
        self.votes = []
        self.total_votes = 0
        self.warns = kwargs.get("warns", 0)
        self.is_warned = False
        self.is_banned = False
        if self.warns > 0:
            if self.warns >= 3:
                self.is_banned = True
            self.is_warned = True
        self._api = kwargs.get("api", SDC())

    async def get_votes(self):
        return await self._api.get_user_votes(user=self)

    async def get_warns(self):
        user = await self._api.get_user_warns(id=self.id)
        if user:
            return user.warns
        else:
            return 0


    def __str__(self):
        return "<User | Name: {0.name}#{0.discriminator}, ID: {0.id}>".format(self)

    def __repr__(self):
        return "<User | Name: {0.name}#{0.discriminator}, ID: {0.id}>".format(self)


class Guild:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "New Guild")
        self.id = kwargs.get("id", "")
        self.description = kwargs.get("des", kwargs.get("description", ""))
        self.invite = kwargs.get("invite")
        self.online = kwargs.get("online", 0)
        self.members = kwargs.get("members", 0)
        self.ups = kwargs.get("upCount", 0)
        self.votes = []
        self.total_votes = 0
        self._api = kwargs.get("api", SDC())


    async def get_place(self):
        return await self._api.get_guild_place(self.id, guild=self)

    async def get_votes(self):
        return await self._api.get_guild_votes(guild=self)


    def __str__(self):
        return "<Guild | Name: {0.name}, ID: {0.id}, Description: {0.description}, Invite: {0.invite}, Members: {0.online}/{0.members}, UPs: {0.ups}, Votes: {0.votes}>".format(self)

    def __repr__(self):
        return "<Guild | Name: {0.name}, ID: {0.id}, Description: {0.description}, Invite: {0.invite}, Members: {0.online}/{0.members}, UPs: {0.ups}, Votes: {0.votes}>".format(self)


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
                        return {}
                    return resp
                elif response.status == 401:
                    raise Exception("Unauthorized")
                else:
                    return {}

    async def get_guild(self, id=None):
        resp = await self._request("get", "guild", id=id)
        resp["id"] = id
        resp["api"] = self
        return Guild(**resp)

    async def get_guild_place(self, *args, **kwargs):
        id = kwargs.get("id")
        if not id:
            id = args[0] if len(args) > 0 else None
        resp = await self._request("get", "guild", id=id, special="place")
        return resp.get("place", -1)

    async def get_guild_votes(self, *args, **kwargs):
        guild = kwargs.get("guild")
        if not isinstance(guild, Guild):
            _id = args[0] if len(args) > 0 else None
            guild = await self.get_guild(kwargs.get("id", _id))
        id = kwargs.get("id", guild.id)
        guild.votes = []
        guild.total_votes = 0
        resp = await self._request("get", "guild", id=id, special="rated")
        if resp:
            for id, count in resp.items():
                vote = Vote(guild=guild, id=id, count=count)
                guild.votes.append(vote)
                guild.total_votes += vote.count
        return guild.votes

    async def get_user_votes(self, *args, **kwargs):
        user = kwargs.get("user")
        if not isinstance(user, User):
            _id = args[0] if len(args) > 0 else None
            user = User(id=kwargs.get("id", _id))
        user.votes = []
        user.total_votes = 0
        resp = await self._request("get", "user", id=user.id, special="rated")
        if resp:
            for id, count in resp.items():
                vote = Vote(guild=id, user=user, count=count)
                user.votes.append(vote)
                user.total_votes += vote.count
        return user.votes
    
    async def get_warns(self):
        resp = await self._request("get", "warns")
        if not resp:
            return None
        type = resp.get("type")
        if type == "user":
            return User(**resp)
        elif type == "guild":
            return Guild(**resp)
        else:
            return None
