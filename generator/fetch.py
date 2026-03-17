import collections
import datetime
import html.parser
import urllib.error
import urllib.parse
import urllib.request

# token values:
STARTTAG = 'STARTTAG'
ENDTAG = 'ENDTAG'
DATA = 'DATA'
COMMENT = 'COMMENT'
DECL = 'DECL'
PI = 'PI'
UNKNOWN = 'UNKNOWN'

HtmlToken = collections.namedtuple('HtmlToken', ('kind', 'tag', 'attrs'))

class HtmlTokenizer(html.parser.HTMLParser):
    def __init__(self, convert_charrefs=True, cdata=None, rcdata=None):
        self.tokens = []
        if cdata is not None:
            self.CDATA_CONTENT_ELEMENTS = cdata
        if rcdata is not None:
            self.RCDATA_CONTENT_ELEMENTS = cdata
        super().__init__(convert_charrefs=convert_charrefs)

    def handle_starttag(self, tag, attrs):
        self.tokens.append(HtmlToken(STARTTAG, tag, dict(attrs)))
    
    def handle_endtag(self, tag):
        self.tokens.append(HtmlToken(ENDTAG, tag, False))

    def handle_startendtag(self, tag, attrs):
        self.tokens.append(HtmlToken(STARTTAG, tag, dict(attrs)))
        self.tokens.append(HtmlToken(ENDTAG, tag, True))

    def handle_data(self, data):
        if not data.isspace():
            self.tokens.append(HtmlToken(DATA, data, None))

    def handle_comment(self, data):
        self.tokens.append(HtmlToken(COMMENT, data, None))

    def handle_decl(self, decl):
        self.tokens.append(HtmlToken(DECL, decl, None))

    def handle_pi(self, data):
        self.tokens.append(HtmlToken(PI, data, None))

    def unknown_decl(self, data):
        self.tokens.append(HtmlToken(UNKNOWN, data, None))

def fetch_url(url, data=None, headers=None):
    if headers is None:
        headers = {}

    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'achievement-hunt/1.0 +https://github.com/madewokherd/Manual'

    req = urllib.request.Request(url, data=data, headers=headers)
    response = urllib.request.urlopen(req)

    return response

def tokenize(data):
    if isinstance(data, bytes):
        data = data.decode('utf8')
    parser = HtmlTokenizer()
    parser.feed(data)
    return parser.tokens

def parse_steam_global_achievement_row(tokens, index):
    # <div class="achieveRow ">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveRow' in tokens[index].attrs['class'])
    index += 1

    # <div class="achieveImgHolder">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveImgHolder' in tokens[index].attrs['class'])
    index += 1

    # img tag
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "img")
    image_url = tokens[index].attrs['src']
    index += 1

    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "img")
    index += 1

    # </div> achieveImgHolder
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    # <div class="achieveTxtHolder">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveTxtHolder' in tokens[index].attrs['class'])
    index += 1

    # <div class="achieveFill">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveFill' in tokens[index].attrs['class'])
    index += 1

    # </div> achieveFill
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    # <div class="achievePercent">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achievePercent' in tokens[index].attrs['class'])
    index += 1

    assert(tokens[index].kind == DATA)
    percentage = float(tokens[index].tag.rstrip('%'))
    index += 1

    # </div> achievePercent
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    # <div class="achieveTxt">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveTxt' in tokens[index].attrs['class'])
    index += 1

    # <h3>
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "h3")
    index += 1

    assert(tokens[index].kind == DATA)
    achievement_name = tokens[index].tag
    index += 1

    # </h3>
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "h3")
    index += 1

    # <h5>
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "h5")
    index += 1

    assert(tokens[index].kind == DATA)
    achievement_description = tokens[index].tag
    index += 1

    # </h5>
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "h5")
    index += 1

    # </div> achieveTxt
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    # </div> achieveTxtHolder
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    return {'name': achievement_name, 'description': achievement_description, 'image_url': image_url, 'percentage': percentage}, index

def parse_steam_global_achievements(tokens, index=0):
    result = []

    while index < len(tokens):
        kind, tag, attrs = tokens[index]

        if kind == STARTTAG and tag == 'div' and 'achieveRow' in attrs.get('class', ''):
            row, index = parse_steam_global_achievement_row(tokens, index)
            result.append(row)
            continue

        index += 1

    return result, index

def fetch_steam_global_achievements(gameid):
    global_achievements_url = f'https://steamcommunity.com/stats/{gameid}/achievements/'

    response = fetch_url(global_achievements_url)

    data = response.read()

    tokens = tokenize(data)

    result, index = parse_steam_global_achievements(tokens)

    return result

def parse_form(tokens, index):
    # <form action="url">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "form")
    url = tokens[index].attrs['action']
    index += 1

    inputs = {}
    while not (tokens[index].kind == ENDTAG and tokens[index].tag == 'form'):
        assert(tokens[index].kind == STARTTAG)
        assert(tokens[index].tag == "input")
        inputs[tokens[index].attrs['name']] = tokens[index].attrs['value']
        index += 1

    query_string = urllib.parse.urlencode(inputs)

    url = f'{url}?{query_string}'

    return url, index + 1;

def fetch_steam_community_posters(gameid):
    url = f'https://steamcommunity.com/app/{gameid}'

    authors = []

    while url:
        response = fetch_url(url)

        data = response.read()

        tokens = tokenize(data)

        url = None

        # we only really care about the author id's, so we can skip any real parsing
        for i in range(len(tokens)):
            if tokens[i].kind == STARTTAG and tokens[i].tag == 'div' and 'apphub_CardContentAuthorName' in tokens[i].attrs.get('class', '') and \
                tokens[i+1].kind != DATA:
                assert(tokens[i+1].kind == STARTTAG)
                assert(tokens[i+1].tag == 'a')
                yield tokens[i+1].attrs['href'].rstrip('/').rsplit('/', 1)[1]

            if tokens[i].kind == STARTTAG and tokens[i].tag == 'form' and tokens[i].attrs.get('id', '').startswith('MoreContentForm'):
                url, _index = parse_form(tokens, i)

def parse_steam_player_achievement_row(tokens, index):
    # <div class="achieveRow ">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveRow' in tokens[index].attrs['class'])
    index += 1

    # <div class="achieveHiddenBox">
    if tokens[index].kind == STARTTAG and tokens[index].tag == 'div' and 'achieveHiddenBox' in tokens[index].attrs.get('class', ''):
        index += 1
        return {'name': '<hidden achievements>', 'unlock_time': None}, index

    # <div class="achieveImgHolder">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveImgHolder' in tokens[index].attrs['class'])
    index += 1

    # img tag
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "img")
    image_url = tokens[index].attrs['src']
    index += 1

    # </div> achieveImgHolder
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    # <div class="achieveTxtHolder">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveTxtHolder' in tokens[index].attrs['class'])
    index += 1

    # <div class="achieveTxt">
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "div")
    assert('achieveTxt' in tokens[index].attrs['class'])
    index += 1

    # <h3>
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "h3")
    index += 1

    assert(tokens[index].kind == DATA)
    achievement_name = tokens[index].tag
    index += 1

    # </h3>
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "h3")
    index += 1

    # <h5>
    assert(tokens[index].kind == STARTTAG)
    assert(tokens[index].tag == "h5")
    index += 1

    assert(tokens[index].kind == DATA)
    achievement_description = tokens[index].tag
    index += 1

    # </h5>
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "h5")
    index += 1

    # </div> achieveTxt
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    unlock_time = None

    # <div class="achieveUnlockTime">
    if tokens[index].kind == STARTTAG and tokens[index].tag == 'div' and 'achieveUnlockTime' in tokens[index].attrs.get('class', ''):
        index += 1

        assert(tokens[index].kind == DATA)
        timestamp = tokens[index].tag.strip()
        try:
            unlock_time = datetime.datetime.strptime(timestamp, 'Unlocked %b %-d, %Y @ %-I:%M%p').replace(tzinfo=datetime.UTC).isoformat()
        except ValueError:
            # implicitly current year
            unlock_time = datetime.datetime.strptime(f'{timestamp} {datetime.datetime.now().year}', 'Unlocked %b %-d @ %-I:%M%p %Y').replace(tzinfo=datetime.UTC).isoformat()
        index += 1

        # <br/>
        assert(tokens[index].kind == STARTTAG)
        assert(tokens[index].tag == "br")
        index += 1

        assert(tokens[index].kind == ENDTAG)
        assert(tokens[index].tag == "br")
        index += 1

        # </div> achieveUnlockTime
        assert(tokens[index].kind == ENDTAG)
        assert(tokens[index].tag == "div")
        index += 1

    # </div> achieveTxtHolder
    assert(tokens[index].kind == ENDTAG)
    assert(tokens[index].tag == "div")
    index += 1

    return {'name': achievement_name, 'unlock_time': unlock_time}, index

def parse_steam_player_achievements(tokens, index=0):
    result = []

    while index < len(tokens):
        kind, tag, attrs = tokens[index]

        if kind == STARTTAG and tag == 'div' and 'achieveRow' in attrs.get('class', ''):
            row, index = parse_steam_player_achievement_row(tokens, index)
            if row['unlock_time']:
                result.append(row)
            continue

        index += 1

    return result, index

def fetch_steam_player_achievements(gameid, player):
    url = f'https://steamcommunity.com/profiles/{player}/stats/{gameid}/achievements/'

    response = fetch_url(url)

    data = response.read()

    tokens = tokenize(data)

    rows, index = parse_steam_player_achievements(tokens)

    # convert to a list of lists of strings, in unlock order
    rows.sort(key = lambda x: x['unlock_time'])

    result = []
    last_ts = ''

    for row in rows:
        name = row['name']
        if row['unlock_time'] == last_ts:
            result[-1].append(name)
        else:
            result.append([name])
            last_ts = row['unlock_time']

    return result

def fetch_steam_achievement_info(gameid):
    global_info = fetch_steam_global_achievements(gameid)

    sequences = []
    for author in fetch_steam_community_posters(gameid):
        seq = fetch_steam_player_achievements(gameid, author)
        if seq:
            sequences.append(seq)
        if len(sequences) >= 20:
            break

    # global achievements are already sorted by percentage, presumably even if the rounded percentage is the same
    sequences.append([[x['name']] for x in global_info])

    return {'achievement_info': global_info, 'sequences': sequences}

