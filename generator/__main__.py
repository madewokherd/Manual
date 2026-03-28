from . import fetch

import argparse
import json
import sys
import urllib.parse

parser = argparse.ArgumentParser(
    prog = "generator",
    description = "Generates a Manual APWorld based on achievement information",
    )

parser.add_argument('url', nargs='*',
    help="One or more URLs used to discover achievement information")

parser.add_argument('--player-ids', nargs='*',
    help="One or more IDs of players used to deduce achievement requirements")

# Output

parser.add_argument('--json-in', type=str,
    help="Read information from JSON instead of fetching it")

parser.add_argument('--raw-json-out', type=str,
    help="Output fetched information in JSON format")

# Steam-specific
parser.add_argument('--steam-app-id', type=int,
    help="The Steam App ID of the game")
parser.add_argument('--steam-players-from-community', type=int,
    help="Number of Steam Community pages to fetch to discover players")

def set_steam_app_id(args, appid):
    steam_app_id = int(appid)
    if args.steam_app_id and args.steam_app_id != steam_app_id:
        print("ERROR: Multiple different steam apps were specified", file=sys.stderr)
        sys.exit(1)
    args.steam_app_id = steam_app_id

def main(argv=None):
    args = parser.parse_args(argv)

    player_ids = args.player_ids or []

    for url in args.url:
        urlparts = urllib.parse.urlparse(url)
        recognized = False
        if len(urlparts.scheme) in (0, 1):
            if args.json_in:
                print("ERROR: Multiple games specified")
                sys.exit(1)
            else:
                args.json_in = url
        elif urlparts.scheme in ('http', 'https'):
            parts = urlparts.path.strip('/').split('/')
            if urlparts.netloc == 'store.steampowered.com':
                if len(parts) >= 2 and parts[0] == 'app' and parts[1].isdigit():
                    set_steam_app_id(args, parts[1])
                    recognized = True
            elif urlparts.netloc == 'steamcommunity.com':
                if len(parts) >= 2 and parts[0] == 'profiles':
                    player_ids.append(parts[1])
                    recognized = True
                    if len(parts) >= 4 and parts[2] == 'stats':
                        set_steam_app_id(args, parts[3])
                        recognized = True
                elif len(parts) >= 2 and parts[0] == 'app':
                    set_steam_app_id(args, parts[1])
                    recognized = True
                elif len(parts) >= 2 and parts[0] == 'stats':
                    set_steam_app_id(args, parts[1])
                    recognized = True
        if not recognized:
            print("ERROR: Unrecognized URL:", url, file=sys.stderr)
            sys.exit(1)

    if sum(1 for argname in ('steam_app_id', 'json_in') if getattr(args, argname)) > 1:
        print("ERROR: Multiple games specified")
        sys.exit(1)
    elif args.steam_app_id:
        community_page_count = args.steam_players_from_community or 0
        info = fetch.fetch_steam_achievement_info(args.steam_app_id, verbose=True, players=player_ids, community_page_count=community_page_count)
    elif args.json_in:
        if args.json_in == '-':
            info = json.load(sys.stdin)
        else:
            with open(args.json_in, 'r') as infile:
                info = json.load(infile)
    else:
        print("ERROR: You must specify a game using a URL, --steam-app-id, or --json-in")
        parser.print_help()
        sys.exit(1)

    if args.raw_json_out:
        if args.raw_json_out == '-':
            sys.stdout.write(json.dumps(info, indent=2))
        else:
            with open(args.raw_json_out, 'w') as outfile:
                outfile.write(json.dumps(info, indent=2))
    else:
        # TODO: Output into src/data
        print(json.dumps(info, indent=2))

if __name__ == '__main__':
    main()

