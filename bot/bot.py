import discord
import os

from draft import *


class MyClient(discord.Client):

    def __init__(self, **options):

        super().__init__(**options)
        self._testing_channel = None
        self._draft_category = None
        self._drafts = {}
        self._dwaynes = []

    async def on_ready(self):
        print("logged on as ", self.user)

        for category in self.guilds[0].categories:
            if category.name == DRAFT_CATEGORY:
                self._draft_category = category

        for channel in self.get_all_channels():
            # if channel.category.name != IGNORED_DRAFT_CHANNEL:
            #     self.drafts.append(Draft(channel))
            if channel.name == 'computer-testing':
                self._testing_channel = channel
        print('Found draft category:', self._draft_category)

        # figure out what drafts are out there already and read them to determine current state of everything
        print('Found draft channels:', self._drafts)

        for potential_dwayne in self.get_all_members():
            if self.user.id == potential_dwayne.id or potential_dwayne.name == 'Carson':
                self._dwaynes.append(potential_dwayne)

        print('Found Dwyanes:', self._dwaynes)

        if self._testing_channel is None:
            raise RuntimeError('Couldn\'t find testing channel')
        # await testing_channel.send('Started')

    async def on_message(self, message):
        if message.author == self.user:
            return

        command = message.content.split(' ')[0]

        if command.startswith(DRAFT_PREFIX):
            draft = await new_draft(message, self._dwaynes, self._draft_category)
            print("Created Draft")
            self._drafts[draft.channel] = draft

        if command.startswith(PICK_PREFIX):
            await self._drafts[message.channel].pick(message)
            print("Pick completed:", message.content)

        if command.startswith(LIST_ROSTER_PREFIX):
            await self._drafts[message.channel].list_rosters()
            print("Listed rosters")

        if command.startswith(FORCE_PICK_PREFIX):
            await self._drafts[message.channel].pick(message, force=True)
            print("Pick completed:", message.content)


if __name__ == '__main__':
    client = MyClient()
    token = os.environ.get('DWAYNE_TOKEN', '')
    client.run(token)