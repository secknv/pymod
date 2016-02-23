import realcookie


class CookieMod:
    rank = 0
    help_dict = {'py_cookie': 'sends a cookie img on channel', 'py_cookie_add': 'add cookie to db from url',
                 'py_cookie_count': 'chat the number of cookies in db', 'py_cookie_rm': 'deletes all the cookies in db'}

    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.cookie = realcookie.cookie()

    async def py_cookie(self):
        try:
            await self.client.send_file(self.message.channel, fp=self.cookie.gib())
        except FileNotFoundError:
            await self.client.send_message(self.message.channel, 'There are no cookies in the database.')

    async def py_cookie_add(self, img_url):
        self.cookie.add(img_url)

    async def py_cookie_count(self):
        cookie_num = self.cookie.count()
        if cookie_num == 1:
            msg = 'There is `1` cookie in the database.'
        else:
            msg = 'There are `' + str(cookie_num) + '` cookies in the database'
        await self.client.send_message(self.message.channel, msg)

    async def py_cookie_rm(self):
        self.cookie.rm()
