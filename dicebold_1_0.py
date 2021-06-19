"""
#################
### ATTENTION ###
#################

Dicebold makes heavy use of f-string formatting. As of writing, f-strings are still fairly new to
Python, so if your system is running Python 3.5 or older, it will not function properly. Please
either update your Python install to 3.6 or later, or since you're looking at my source code,
feel free to edit to the string formatting method of your choice. I made this for fun,
I don't care if you modify it to get around updating your Python version, as long as you still
give credit.

---------------------------------------------------------------------------------------------------

Dicebold is a simple Discord bot for generating random numbers, with formatting stylized as dice
rolls in a tabletop game. The purpose was to design a bot that has clean, simple code we can
ensure is running honestly and consistently to remove any concerns around suspicious "rolls".

PROPER ROLL FORMATTING:

-roll 1d20
!roll 2d6 + 5
/roll 7d4 - 4

The number prior to the "d" represents how many dice you want to roll. The number after it
represents the type of die/integer range you're looking for."""

# TODO: Handling for multiple dice types per roll, add name to result, better result formatting.

import os
import re as regex
import secrets
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Gets the token the bot uses for its API access.

client = discord.Client()


def roller(die_num, die_type):
    """Returns a list of rolls of the appropriate die type. If the specified die is invalid
    (ie, a fish-sided die) the ValueError is thrown, and roller returns none."""
    counter = 0
    rolls = []

    while counter < die_num:
        try:
            rolls.append(secrets.randbelow(die_type)+1)
            # +1 needs to be added in order to ensure the value is in the appropriate range.
            # (ie, an attempt to roll a six-sided die will generate a number between 0 and 5,
            # +1 turns that into 1-6.)
            counter += 1
        except ValueError:
            return None
    return rolls


def modcheck(i):
    """Checks whether or not there's a modifier beyond the die roll that needs to be
    stored in a string."""
    try:
        int(i)
    except ValueError:
        return False
    return True


@client.event
async def on_message(message):
    """Runs the logic for checking messages for its call to post."""
    if message.content.lower().startswith("!roll") or \
            message.content.lower().startswith("-roll") or \
            message.content.lower().startswith("/roll"):
        # Responds to three common dice-rolling commands to minimize confusion.
        channel = message.channel
        # Records the channel to respond in.

        roll_cmd = message.content.replace(" ", "")[5:]
        # Takes the command, strips out whitespace, and removes the roll command so only the roll
        # type specifiers are taken.

        failsafe_triggered = False
        # Todo: Find a better way to handle fail states for roll commands.
        # here may be a more efficient way of doing this, but this works for now. Ensures the bot
        # doesn't try to post a roll when the user gives invalid input.

        num_of_dice = 0
        type_of_dice = 0
        modifier = None

        try:
            num_of_dice = int(roll_cmd[:roll_cmd.index("d")])
        except ValueError:
            await channel.send("**Error**: Not a valid die number! Please only use whole numbers!")
            failsafe_triggered = True
            # Checks for the number of dice the user is rolling. If an invalid number of dice
            # is given (ie, -roll fishd20), the user is told as much asn failsafe is triggered.

        if modcheck(roll_cmd[roll_cmd.index("d")+1:]):
            # Checks whether there's any modifier that needs to be recorded beyond the die roll.
            type_of_dice = int(roll_cmd[roll_cmd.index("d")+1:])
        else:
            operation = regex.compile(r"[+*\-/]")
            # Sets up a regular expression to record any type of mathematical operation.
            modifier = roll_cmd[regex.search(operation, roll_cmd).start():]
            # Captures any text from a mathematical operator onward to be stored for use further.
            try:
                type_of_dice = int(roll_cmd[roll_cmd.index("d")+1:
                                            regex.search(operation, roll_cmd).start()])
                # Records the number of dice to roll.
            except ValueError:
                await channel.send("**Error**: Not a valid die type! "
                                   "Please only use whole numbers!")
                failsafe_triggered = True
                # See previous ValueError. Same purpose, but with die type rather than die number.

        if not failsafe_triggered:
            # Checks to make sure it only fires if the failsafe isn't triggered. The failsafe fires
            # when the bot gives an error message for an invalid roll command.
            result_array = roller(num_of_dice, type_of_dice)
            # Uses the roller methods to generate a set of die rolls.
            if result_array is None:
                await channel.send("**Error**: Invalid die type. Please only use whole numbers!")
                # roller returns None if an invalid expression is submitted.
                # Redundant safety is important.
            elif modifier is None:
                await channel.send(f"Roll results: {result_array}\n\nRoll total: "
                                   f"{sum(result_array)}")
                # Returns a modifier-free roll.
            else:
                await channel.send(f"Roll results: {result_array}\n\n"
                                   f"Roll total with modifiers: "
                                   f"{eval(f'{sum(result_array)}{modifier}')}")
                # Returns a roll, then uses eval() to record the result with modifier applied.
                #
                # #################
                # ### ATTENTION ###
                # #################
                #
                # As a general rule, using eval() on user input is not advisable. It is an easily
                # abused function that is vulnerable to exploitation by a malicious user. It is
                # used here because this bot is intended for use in small groups amongst friends
                # and known individuals, so there is not a substantial risk in its intended use
                # case.
                #
                # IF YOU INTEND TO USE DICEBOLD'S CODE FOR YOUR OWN PURPOSES, PLEASE BE AWARE OF
                # THIS VULNERABILITY AND USE A DIFFERENT< MORE SECURE IMPLEMENTATION.


client.run(TOKEN)
# Runs the bot's client session  using its token.
