"""

#####################
### VERSION 1.4.0 ###
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

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
# New versions of Discord's API require explicitly specifying non-default permissions for bots,
# including permission to read messages.

client = discord.Client(intents=intents)


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


def flip1():
    """Extremely simple method. Generates a random number between 0 and 999, then checks whether
    that number is even of odd. Even numbers return a coin flip that results "heads", odd numbers
    return a coin that results "tails." Not entirely necessary, but it's a nice little thing for
    style points."""
    flip_value = secrets.randbelow(1000)
    if flip_value % 2 == 0:
        return "heads"
    return "tails"


def flipmany(coin_count):
    """Basically the same concept as flip1, just expanded to accept a variable, and then flip that
    many coins. In theory flip1 can be removed and replaced with a flipmany(1) call, but it lets me
    style it a bit more cleanly, and it's a four-line method, it's not like it's making substantial
    bloat."""
    flip_array = []
    i = 0
    while i < int(coin_count):
        flip_array.append(secrets.randbelow(1000))
        i += 1
        # Performs the flipping operation the specified number of times.
    output_array = []
    # Output array for storing "translated" results.

    for coinflip in flip_array:
        if coinflip % 2 == 0:
            output_array.append("heads")
        else:
            output_array.append("tails")
            # Populates output_array with the "heads" and "tails" calls for each flip operation, so
            # you get "The coin was heads" instead of "The coin was 674"
    return output_array


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

        critmod = regex.compile(r"[x*][1-6]")

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

    elif message.content.lower().startswith("!flip") or \
            message.content.lower().startswith("-flip") or \
            message.content.lower().startswith("/flip"):
        # Responds to a coinflip command.
        channel = message.channel
        # Grabs channel ID
        output_string = ""
        flip_result = None
        if len(message.content.lower()) == 5:
            # Processes a single flip if the user only wants to flip one coin. Since we already know
            # our command is starting with "-flip" or something similar, we know that will always be
            # the first five characters of the message. If those are the only characters in the
            # message, we interpret that as a single coin flip.
            flip_result = flip1()
            output_string = f"**{set_username(message.author)}** flipped **a coin!**\n\n" \
                            f"The result was **{flip_result}!**"
        else:
            # Basically the above, but with the addiitonal logic isolating the coin_count variable
            # for flipmany.
            coin_num = message.content.lower().replace(" ", "")[5]
            flip_result = flipmany(coin_num)
            output_string = f"**{set_username(message.author)}** flipped " \
                            f"**{coin_num} coins!**\n\n" \
                            f"The result was **{flip_result}!**"
        await channel.send(output_string)

    elif message.content.lower().startswith("!statroll") or \
            message.content.lower().startswith("-statroll") or \
            message.content.lower().startswith("/statroll"):
        # Responds to a statroll command.
        channel = message.channel
        # Grabs channel ID
        reroll = False
        # Allows to check if the user wants to reroll ones in their stat rolls. False by default.
        if "-rr1" in message.content.lower():
            reroll = True
            # Sets reroll to true if the user selected to reroll their ones.
        raw_rolls = [roller(4, 6), roller(4, 6), roller(4, 6), roller(4, 6), roller(4, 6),
                     roller(4, 6)]
        # Generates a standard ability score array for a D20 system TTRPG.
        if reroll:
            # Checks if the user wanted to reroll their ones.
            for roll in raw_rolls:
                # Runs through each roll in raw_rolls.
                die_number = 0
                while die_number < 4:
                    # Uses die_number to iterate through all four rolls in a given roll before
                    # continuing to the next ability roll.
                    while roll[die_number] == 1:
                        roll[die_number] = roller(1, 6)[0]
                        # Rerolls any number in the current ability roll that is equal to one, then
                        # makes sure that the reroll isn't also a 1 - hence using "while" instead of
                        # "if" - and once a non-one number is in, exits the while statement.
                    die_number += 1
                    # Increments die_number to continue through this ability roll. Resets every time
                    # it moves onto the next stat roll by re-declaring die_number to zero.
        stats_array = []
        # Stores final values.
        output_string = f"Rolling ability scores for **{set_username(message.author)}!**\n\n"
        count = 0

        for roll in raw_rolls:
            # Runs through each roll.
            output_string += f"First roll: **{raw_rolls[count]}**, "
            # Adds the initial four die rolls to output_string.
            roll.remove(min(roll))
            stats_array.append(sum(roll))
            # Removes the lowest roll from the ability score in-question, as per typical D20 system
            # rules, then sums the remaining dice and adds that to the stat array.
            output_string += f"resulting score **➔ {stats_array[count]}**\n"
            # Adds the "final" value for this roll to output_string.
            count += 1
            # Increments to assign the proper values. In theory this could all be done without
            # using an incrementing integer, but it makes the formatting of the final output
            # message a lot cleaner and easier.

        output_string += f"\n**Ability score rolls for {set_username(message.author)}: " \
                         f"{stats_array}**"
        # Appends the final statement with all six ability scores to output_string. Technically this
        # is redundant since they're all displayed individually earlier in the message, but this
        # gives a nice look to the message.
        await channel.send(output_string)
    """Below is just me being cheeky. Don't worry about it."""
    # elif message.content.lower().startswith("good to have you back"):
    #     channel = message.channel
    #     msg = ""
    #     if str(message.author) == "REDACTED":
    #         msg = "Good to be back, boss!"
    #     else:
    #         msg = f"Thanks, {set_username(message.author)}!"
    #     await channel.send(msg)


client.run(TOKEN)
