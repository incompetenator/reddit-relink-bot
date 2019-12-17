# Written by fyssion
# https://www.github.com/fyssion
# See LICENSE for license details.


# Libraries
from discord.ext import commands
import discord
import praw
import coloredlogs, logging
import yaml
import re
from datetime import datetime as d

from cogs.utils import wait_for_deletion


def get_prefix(client, message):
    
    prefixes = ['rr!!']

    return commands.when_mentioned_or(*prefixes)(client, message)

class ReLink(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            description="A bot that detects any Reddit links and relinks them in clickable fashion.",
            owner_id=224513210471022592,
            case_insensitive=False
        )



        #Config.yml load
        with open("config.yml", 'r') as config:
            try:
                self.data = yaml.safe_load(config)

            except yaml.YAMLError as exc:
                self.log.critical("Could not load config.yml")
                print(exc)
                quit()

        

        
        # Cogs
        self.cogsToLoad = ["cogs.subreddit", "cogs.redditor"]

        # Listeners
        self.add_listener(self.on_mention, 'on_message')

        # Logging
        self.log = logging.getLogger(__name__)
        coloredlogs.install(level='DEBUG', logger=self.log, fmt='(%(asctime)s) %(levelname)s %(message)s', datefmt='%m/%d/%y - %H:%M:%S %Z')

        # Other Variables
        self.auto_deletion_message = "This message auto-deletes after 30 seconds."
        self.reddit_color = 0xFF4301
        self.warning_color = 0xFFCC4D




    
    async def on_mention(self, message):
        """
        Responds to a mention with a tiny "help menu."
        It's not really a help menu.
        """

        if message.content == f"<@{self.user.id}>" or message.content == f"<@!{self.user.id}>":

            msg = "Hey there, " + message.author.mention + "!\nI'm a bot that detects any Reddit links and relinks them in clickable fashion!\
            \n\nI support relinking subreddits (`r/SUBREDDIT`) and users (`u/USER`).\
            \n\nEvery message I send (including this one) automatically deletes after 30 seconds.\
            \nIf you want to delete the message sooner, just click the :x: reaction.\
            \nIf you want to keep the message, just react with :pushpin:, and I'll save it for you.\
            \n\n[Visit my GitHub Repository for more info.](https://github.com/incompetenator/reddit-relink-bot)"


            em = discord.Embed(
                description=msg,
                color=self.reddit_color
                )
            em.set_footer(
                text = self.auto_deletion_message,
                icon_url = self.user.avatar_url
                )
                
            try:
                bot_message = await message.channel.send(embed=em)
                self.loop.create_task(
                    wait_for_deletion(bot_message, user_ids=(message.author.id,), client=self)
                )
            except discord.errors.Forbidden:
                self.log.error(f"Bot does not have permission to send messages in channel: '{str(message.channel)}'")
    




    async def loginToReddit(self, id, secret):
        """
        Logs the bot into reddit and creates a reddit instance.
        If the bot isn't logged in, the bot force quits.
        """

        self.reddit = praw.Reddit(client_id = id,
                            client_secret = secret,
                            user_agent = 'my user agent'
                            )
        if self.reddit.read_only == True:
            self.log.info("Logged into Reddit")
            return

        self.log.critical("Not logged into Reddit!")
        await self.logout()
        quit()




    async def on_ready(self):

        self.log.info(f'Logged in as {self.user.name} - {self.user.id}')
            
        self.startup_time = d.now()

        self.remove_command('help') # Don't need it!

        await self.loginToReddit(self.data['reddit_client_id'], self.data['reddit_client_secret'])

        for cog in self.cogsToLoad:
            self.load_extension(cog)

        self.load_extension("jishaku") # For debugging




    
    def run(self):
        super().run(self.data['discord_token'], reconnect=True, bot=True)
    

bot = ReLink()
bot.run()
