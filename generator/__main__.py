
import argparse

parser = argparse.ArgumentParser(
    prog = "generator",
    description = "Generates a Manual APWorld based on achievement information",
    )

parser.add_argument('url', nargs='*',
    help="One or more URLs used to discover achievement information")

# Steam-specific
parser.add_argument('--steam-app-id', nargs=1, type=int,
    help="The Steam App ID of the game")

parser.print_help()

