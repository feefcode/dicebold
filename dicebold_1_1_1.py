"""

#####################
### VERSION 1.1.1 ###
#####################

#####################
##### ATTENTION #####
#####################

Dicebold makes heavy use of f-string formatting. As of writing, f-strings are still fairly new to
Python, so if your system is running Python 3.5 or older, it will not function properly. Please
either update your Python install to 3.6 or later, or since you're looking at my source code,
feel free to edit to the string formatting method of your choice. I made this for fun,
I don't care if you modify it to get around updating your Python version, as long as you still
give credit.

PLEASE ALSO NOTE THAT DICEBOLD MAKES HEAVY USE OF EVAL() ON USER INPUT. As a general rule, this is
not advisable. It is an easily abused function that is vulnerable to exploitation by a malicious
user. It is used here because this bot is intended for use in small groups amongst friends and
known individuals, so there is not a substantial risk in its indended use case.

IF YOU INTEND TO USE DICEBOLD'S CODE FOR YOUR OWN PURPOSES, PLEASE BE AWARE OF THIS VULNERABILITY
AND USE A DIFFERENT, MORE SECURE IMPLEMENTATION.

---------------------------------------------------------------------------------------------------

Dicebold is a simple Discord bot for generating random numbers, with formatting stylized as dice
rolls in a tabletop game. The purpose was to design a bot that has clean, simple code we can
ensure is running honestly and consistently to remove any concerns around suspicious "rolls".

PROPER ROLL FORMATTING:

-roll 1d20
!roll 2d6 + 5
/roll 7d4 - 4
-roll d20, 2d6 + 3 x2

The number prior to the "d" represents how many dice you want to roll. The number after it
represents the type of die/integer range you're looking for."""

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
    stored in a string. TRUE = successful int conversion, no modifiers. FALSE = failed int
    conversion, modifiers exist."""
    try:
        int(i)
    except ValueError:
        return False
    return True


def set_username(author):
    """Sets the appropriate username for the roll output based on whether or not the user has a
    nickname, or if it's a DM."""
    try:
        if author.nick is not None:
            return author.nick
        # Sets the username to on-server nickname. If author.nick is None, they don't have a server
        # specific nickname, so it moves onto their actual Discord name in the line below.
        return author.name
    except AttributeError:
        return author.name
    # Since author.nick does not exist for direct messages, trying to DM the bot will create an
    # AttributeError. By restating line 77 in an except block, it is able to handle that error
    # cleanly and respond to a DM'd roll command.


def extract_roll(roll_expression):
    """Takes our regular expression for a roll and extrapolates the number of dice/dice type into
    a list to be used."""
    if roll_expression[0] == "d":
        extracted_rolls = [1, int(roll_expression[roll_expression.index("d")+1:])]
        # Checks if it got a "d20" roll instead of a "1d20" roll. If so, automatically sets its
        # die-number value to 1.
    else:
        extracted_rolls = [int(roll_expression[:roll_expression.index("d")]),
                           int(roll_expression[roll_expression.index("d")+1:])]
    return extracted_rolls


def string_recompile(string_to_use, rolls_to_insert, dice_exp):
    """Cuts up the user's command, replaces the die-roll expressions with the results, then returns
    a string with the dice properly rolled."""

    sliced = regex.split(dice_exp, string_to_use)
    # Cuts up the command expression, using the dice-roll expressions as "markers." Sliced is a list
    # of each piece of the string other than the roll expressions.

    return_string = ""

    while len(sliced) != 0:
        # Ensures the loop stops operating once everything from sliced has been reinserted.
        return_string += sliced.pop(0)
        # Inserts the current first element in sliced, then removes it from the list.
        if len(rolls_to_insert) != 0:
            # Checks if there are any remaining rolls to insert.
            return_string += str(rolls_to_insert.pop(0))
            # If there are rolls to insert, appends the one currently in the first element, then
            # removes it.

    return return_string


def command_processor(cmd_string, roll_exp, cmd_user, critmod):
    """Handles the majority of processing for a given command. Storing it in a method instead of
    doing it sequentially in the "main" method lets you reuse it for multiple rolls in a single
    command."""

    dice_to_roll = regex.findall(roll_exp, cmd_string)
    # Creates a list of all matches with the regular expression for a die roll.

    rolls = []
    output = ""
    user = set_username(cmd_user)

    critifier = 0

    if regex.search(critmod, cmd_string) is not None:
        critifier = int(cmd_string[-1])
        cmd_string = cmd_string[:-2]
        # Checks for a critmod expression. If one is found, changes critifier to the appropriate
        # value, and removes the modifier from the command for eval's sake.

    for roll in dice_to_roll:
        roll_result = roller(extract_roll(roll)[0], extract_roll(roll)[1])
        rolls.append(sum(roll_result))
        if roll[0] == "d":
            output += f"**{user}** rolled **1{roll}** ➔ {roll_result}\n\n"
        else:
            output += f"**{user}** rolled **{roll}** ➔ {roll_result}\n\n"
        # Calls roller to roll each die, using extract_roll to figure out how to roll it. Then, sums
        # the rolls of that die and adds them to the rolls list, and finally adds a prompt
        # explaining its actions to the output string. If-else checks the formatting of the user's
        # input to ensure clean, pleasant-to-read output regardless of input formatting.

        if len(regex.sub(roll_exp, "", cmd_string)) == 0 and critifier == 0:
            return f"{output}**Roll total ➔ {sum(rolls)}**"
        # Allows for stylization of output text based on whether or not there is a modifier.

        if critifier == 0:
            # Checks if any crit mod was recorded. If not, it prints the following. Otherwise, it
            # skips this return statement and moves onto the next one.
            return f"{output}**Roll total with modifiers ➔ " \
                   f"{eval(str(string_recompile(cmd_string, rolls, roll_exp)))}**"
        return f"{output}***CRITICAL HIT ! ! !***\n\n**Roll total with modifiers ➔ " \
               f"{eval(str(string_recompile(cmd_string, rolls, roll_exp)))*critifier}**"
        # Stylized output for if there is a crit mod recorded.


@client.event
async def on_message(message):
    """Checks the user's message and routes the command as appropriate."""
    if message.content.lower().startswith("!roll") or \
            message.content.lower().startswith("-roll") or \
            message.content.lower().startswith("/roll"):
        # Responds to three common dice-rolling commands to minimize confusion.

        channel = message.channel
        # Responds to three common dice-rolling commands to minimize confusion.

        roll_cmd = message.content.lower().replace(" ", "")[5:]
        # Takes the command, strips out whitespace, and removes the roll command so only the roll
        # type specifiers are taken.

        roll_exp = regex.compile(r"\d{1,4}d\d{1,4}")
        roll_exp2 = regex.compile(r"d\d{1,4}")

        critmod = regex.compile(r"x[1-6]")

        output_string = ""

        invalid_cmd = "**ERROR:** Please provide a valid die roll command."

        if not regex.search(roll_exp, roll_cmd) and not regex.search(roll_exp2, roll_cmd):
            await channel.send(invalid_cmd)

        if "," in roll_cmd:
            # Commas are used to denote multiple rolls in a single command. Allows for fully
            # separate rolls without multiple commands.
            commands_to_process = roll_cmd.split(",")
            # Creates a list of commands to process, using the comma to note where one ends and the
            # next begins.

            for command in commands_to_process:
                if len(output_string) != 0:
                    # Allows nice, clean formatting by checking whether this is the first line to
                    # be added to the output string. After that, uses the appropriate command
                    # processor call to process that command.
                    if regex.search(roll_exp, command):
                        output_string += "\n\n"+command_processor(command, roll_exp, message.author,
                                                                  critmod)
                    elif regex.search(roll_exp2, command):
                        output_string += "\n\n"+command_processor(command, roll_exp2,
                                                                  message.author, critmod)
                        # These if-elif blocks check to see which roll expression the user's input
                        # matches, in order to ensure it is processed properly. This is also true
                        # for the if-elifs in each of the two following else-blocks.
                else:
                    if regex.search(roll_exp, command):
                        output_string += command_processor(command, roll_exp, message.author,
                                                           critmod)
                    elif regex.search(roll_exp2, command):
                        output_string += command_processor(command, roll_exp2, message.author,
                                                           critmod)
        else:
            if regex.search(roll_exp, roll_cmd):
                output_string += command_processor(roll_cmd, roll_exp, message.author, critmod)
            elif regex.search(roll_exp2, roll_cmd):
                output_string += command_processor(roll_cmd, roll_exp2, message.author, critmod)

        await channel.send(output_string)


client.run(TOKEN)
