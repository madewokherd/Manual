import argparse
import sys
import urllib.parse

parser = argparse.ArgumentParser(
    prog = "generator",
    description = "Generates a Manual APWorld based on achievement information",
    )

parser.add_argument('url', nargs='*',
    help="One or more URLs used to discover achievement information")

# Steam-specific
parser.add_argument('--steam-app-id', type=int,
    help="The Steam App ID of the game")

def main(argv=None):
    args = parser.parse_args(argv)

    for url in args.url:
        urlparts = urllib.parse.urlparse(url)
        recognized = False
        if len(urlparts.scheme) in (0, 1):
            pass # TODO: handle json filename
        elif urlparts.scheme in ('http', 'https'):
            if urlparts.netloc == 'store.steampowered.com':
                parts = urlparts.path.strip('/').split('/')
                if len(parts) >= 2 and parts[0] == 'app' and parts[1].isdigit():
                    steam_app_id = int(parts[1])
                    if args.steam_app_id and args.steam_app_id != steam_app_id:
                        print("ERROR: Multiple different steam apps were specified", file=sys.stderr)
                        sys.exit(1)
                    args.steam_app_id = steam_app_id
                    recognized = True
        if not recognized:
            print("ERROR: Unrecognized URL:", url, file=sys.stderr)
            sys.exit(1)

    print(args.steam_app_id)

if __name__ == '__main__':
    main()

