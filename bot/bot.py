import discord
import os

class MyClient(discord.Client):

    def __init__(self, **options):

        super().__init__(**options)
        self.testing_channel = None

    async def on_ready(self):
        print("logged on as ", self.user)
        for channel in self.get_all_channels():
            print(channel)
            if channel.name == 'computer-testing':
                testing_channel = channel

        if testing_channel is None:
            raise RuntimeError('Couldn\'t find general channel')
        await testing_channel.send('Started')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == 'mal':
            await message.channel.send('computer')

if __name__ == '__main__':
    client = MyClient()
    token = os.environ.get('DWAYNE_TOKEN', '')
    client.run(token)