import random

DRAFT_PREFIX = '/new-draft'
PICK_PREFIX = '/pick'
LIST_ROSTER_PREFIX = '/rosters'
FORCE_PICK_PREFIX = '/force-pick'
DRAFT_CATEGORY = 'drafts'
IGNORED_DRAFT_CHANNEL = 'dead-dove-do-not-eat' # sekrit draft channel to ensure it can always find draft category


async def new_draft(message, dwaynes, category):

    draft_channel = normalize(message, DRAFT_PREFIX)
    print('Creating draft with topic', draft_channel)
    draft = Draft(await message.guild.create_text_channel(name=draft_channel, category=category), dwaynes)
    await(draft.show_draft_order())
    return draft


def normalize(message, prefix):
    return message.content.lstrip(prefix).strip().replace(' ', '-')


def nickname_else_name(user):
    return user.nick if user.nick is not None else user.name


class Draft:
    """
    Class for representing a draft. One day this might be a database table, but for now the state (order and
    picks) will be in the channel and this class will read it on startup.
    """

    def __init__(self, channel, dwaynes):
        self.channel = channel
        rounds = 5
        order = dwaynes.copy()
        random.shuffle(order)
        self._initial_order = order.copy()
        self._order = []
        for _ in range(rounds):
            self._order += order
            order.reverse()
        print(channel.name,  'Draft order:', ', '.join([nickname_else_name(dwayne) for dwayne in self._order]))

        self._current_pick = 0
        print(dwaynes)
        self._picks = {dwayne: [] for dwayne in dwaynes}

    async def notify_on_clock(self):

        await self.channel.send('Your pick ' + self._order[self._current_pick].mention)

    async def pick(self, message, notify=True, force=False):

        if self.is_over():
            await self.channel.send('The draft is over already!')
            await self.list_rosters()

        pick = normalize(message, PICK_PREFIX if not force else FORCE_PICK_PREFIX)

        picker = message.author if not force else self._order[self._current_pick]
        self._picks[picker].append(pick)
        self._current_pick += 1

        if self.is_over():
            await self.channel.send('Draft complete!')
            await self.list_rosters()
        else:
            if notify:
                await self.notify_on_clock()

    async def show_draft_order(self):

        print(self._initial_order)
        await self.channel.send('Draft order:\n' + '\n'.join([nickname_else_name(dwayne)
                                                              for dwayne in self._initial_order]))
        await self.notify_on_clock()

    async def list_rosters(self):

        await self.channel.send('Rosters:\n' + '\n'.join(
            [nickname_else_name(dwayne) + ': ' + ', '.join(self._picks[dwayne]) for dwayne in self._initial_order]
        ))

    def is_over(self):
        return self._current_pick == len(self._order)

