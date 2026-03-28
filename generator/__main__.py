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
            pass # TODO: handle json filename
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

    if args.steam_app_id:
        community_page_count = args.steam_players_from_community or 0
        info = fetch.fetch_steam_achievement_info(args.steam_app_id, verbose=True, players=player_ids, community_page_count=community_page_count)
    else:
        print("ERROR: You must specify a game using a URL or --steam-app-id")
        parser.print_help()
        sys.exit(1)

    print(json.dumps(info, indent=2))

if __name__ == '__main__':
    main()

