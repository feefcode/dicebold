# # # # # # # # # # # # # #
# # # ATTENTION ! ! ! # # #
# # # # # # # # # # # # # #
# Dicebold makes heavy use of f-string formatting. As of writing, f-strings are still fairly new to Python, so if your
# system is running Python 3.5 or older, it will not function properly. Please either update your Python install to
# 3.6 or later, or since you're looking at my source code, feel free to edit to the string formatting method of your
# choice. I made this for fun, I don't care if you modify it to get around updating your Python version, as long as you
# still give credit.

import random

test_string1 = "/roll 1d20 + 5"
test_string2 = "/roll 1d6- 3"
test_string3 = "/roll 2d12 +7+4"
test_strings = [test_string1, test_string2, test_string3]

test_roll1 = "/roll 1d6"
test_roll2 = "/roll 2D10"
test_roll3 = "/roll 3 d20"
test_roll4 = "-roll 1d100"
ely_roll = "!roll 1d20"
test1 = [test_roll1, test_roll2, test_roll3, test_roll4, ely_roll]


def roll_dice(roll_string):
    if roll_string.lower().startswith("/roll"):
        # Checks to make sure the line is actually meant to be evaluated for a die roll. Other bots have used "-roll"
        # and "!roll," this one uses "/roll."
        space_free_string = roll_string.replace(" ", "")
        space_free_string = space_free_string.lower()
        # In order to make things as uniform and easy to process for the bot as possible, all white space is removed,
        # and everything is converted to lower-case.
        if "d" in space_free_string:
            # Checks to make sure a valid die roll has been specified.
            die_marker = space_free_string.index("d")
            number_of_dice = int(space_free_string[die_marker-1])
            die_type = 0
            later_operation = ""
            # die_marker records the position of the "d" in the expression. (1d8, 2d10, etc.) This allows easy pinning
            # down of both the number of dice and the die type, as it immediately follows the former, and immediately
            # precedes the latter. die_type and number_of_dice are extremely self-explanatory. later_operation is an
            # empty string that will be used to store any further mathematical operations.

            if "+" in space_free_string:
                die_type = int(space_free_string[die_marker+1:space_free_string.index("+")])
                later_operation = space_free_string[space_free_string.index("+"):]
            elif "-" in space_free_string:
                die_type = int(space_free_string[die_marker+1:space_free_string.index("-")])
                later_operation = space_free_string[space_free_string.index("-"):]
            else:
                die_type = int(space_free_string[die_marker+1:])
            # This if-elif-else set checks whether the roll has a modifier, and if it does, whether it's positive or
            # negative. In either case, the math for the roll's modifier is saved in later_operation, and the type of
            # die being rolled is recorded in die_type.

            all_rolls = []
            i = 0
            while i < number_of_dice:
                another_roll = random.randint(1, die_type)
                all_rolls.append(another_roll)
                i += 1
            roll_total = 0
            for item in all_rolls:
                roll_total += item
            # all_rolls is an empty array for storing each roll, while roll_total is an integer that gets the combined
            # total of all the dice rolls in this roll. This allows the program to have a clear record of each roll's
            # individual value, the combined total of all of the rolls, and perform the operations in a way that can be
            # adapted to any number of dice being used with a simple while-loop and for-loop combo.

            return f"You want to roll {number_of_dice} d{die_type}! Your rolls are {all_rolls.__str__()}!\n" \
                   f"With modifiers, your roll is {eval(f'{roll_total}{later_operation}')}!\n"
            # Returns a string of text telling what dice were rolled, how many were rolled, what each roll's total was,
            # and what the combined total is after performing the modifier operations, courtesy of an eval statement.
            # Final release version will have a cleaner, more concise output, but this is nice and clear and easy to
            # debug and find issues inside of. Please note that eval, while an effective way of turning text strings
            # into a math operation, is extremely insecure. Because of this, Dicebold should not be used for any
            # sensitive, secure random number generation. That said, I don't think hackers or the FBI care that you
            # rolled a nat 1 when you tried to seduce the black dragon, so it's fine here.
        else:
            return "Please specify a valid die roll!"
            # Yells at idiots who don't input proper dice values.
    else:
        return f"Invalid roll request \"{roll_string}\". This is shown because this is a test, in the actual bot, this " \
               f"line will be ignored and have no response."
        # Yells at idiots who don't input proper roll requests. Given this will be removed from the final version, the
        # only potential idiot here is me.


for string in test1:
    print(roll_dice(string)+"\n")

for string in test_strings:
    print(roll_dice(string))
