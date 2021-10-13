import re


def remove_patterns(string):
    patterns = [
        '([A][n]*)([^.]*)(Deck Building Game)',
        '(First|Second|Third|Fourth|Fifth|Sixth|Seventh)\s*Edition',
        '(Primeira|Segunda|Terceira|Quarta|Quinta|Sexta|Sétima)\s*Edição',
        '[\(\[].*?[\)\]]',
        '[0-9]{5,}',
        '[0-9]+\s*–\s*[0-9]+',
        '[0-9]+-[0-9]+',
    ]

    for pattern in patterns:
        compiled = re.compile(pattern)
        search = re.search(pattern, string)

        if search:
            try:
                string = re.sub(search.group(3), '', string, flags=re.IGNORECASE)
                string = re.sub(search.group(1), '', string, flags=re.IGNORECASE)

            except IndexError:
                string = re.sub(compiled, '', string)

    return string


def remove_special_chars(string):
    special_chars = [
        '?', '"', "'", '!', '¡', ',', 'ª',
        '.', '‘', '¿', '{', '[', '}', ']',
        '_', '#', '½', '+', '*', '%', 'º', 
        '°',
        'The Board Game',
        'The Boardgame',
        'The BoardGame',
        'Boardgame',
        'BoardGame',
        'Board Game',
        'The Deckbuilding Game'
        'Deck-Building Game',
        'Expansion Pack',
        'Expansion pack',
        'Expansion',
        'expansion',
        'Volume',
        'Vol.',
        'Vol',
        'The Miniatures Game',
        'Tabletop Miniatures Game',
        'Miniatures Game',
        'The Card Game',
    ]

    for char in special_chars:
        string = string.replace(char, '')

    return string


def replace_numbers(string):
    if 'Warhammer' in string:
        string = string.replace('Warhammer 40000', 'Warhammer 40k')

    pattern = re.compile('\s+[0-9]*:')
    string = re.sub(pattern, ':', string)

    return string


def process_special_chars(string):
    mapping = {
        'ö': 'o', 'à': 'a', 'ū': 'u', '&': 'N',
        '$': 's',
        'The Roleplaying Game': 'RPG',
        'Roleplaying Game':     'RPG',
        'Role Playing Game':    'RPG',
        'X-Wing':               'XWing',
        'Y-Wing':               'YWing',
        'Set #':                'Set',
    }

    for special, letter in mapping.items():
        string = string.replace(special, letter)

    return string


def merge_hyphens(string):
    index = string.find('-')

    try:
        if index > 0:
            if string[index-1] != ' ' and string[index+1] != ' ':
                string = string.replace('-', '')

    except IndexError:
        pass

    return string


def split_into_tags(string):
    chars = [
        ':', '/', '\\', '–', '-', '—', '-'
    ]

    string = string.replace(' ', '')
    string = string.replace('-', ' #')
    string = string.strip()

    for char in chars:
        string = string.replace(char, ' #')

    string = '#' + string

    return string


def manage_series(string):
    series = {
        'Pandemic',             'Dungeons & Dragons',   'Zombicide',            'Zpocalypse',
        'Zooloretto',           'Wings of Glory',       'World of Darkness',    'Black Plague',
        'Green Horde',          'Zombie Dice',          'The Boardgame',        'Zombie Fluxx',
        'DC',                   'Marvel',               'GURPS',                'Star Wars',
        'O Senhor dos Anéis',   'A Guerra dos Tronos',  'Guerra dos Tronos',    'Tiny Epic',
        'Invader',              'Dark Side',            'Bang',                 'Encantados',
        'Exploding Kittens',    'Ticket to Ride',       'Clank',                '7 Wonders',
        'Fronteira do Império', 'Lenda dos Cinco Anéis','Viticulture',          'El Grande',
        'Pathfinder',           'Tormenta',             'T.I.M.E.',             'Advanced Dungeons & Dragons',
        'Achtung',              'Kick-Ass',             'CO2'                   'Dungeon World',
        'Chamado de Cthulhu',   'Tiny Dungeon',         'Ubongo',               'Warhammer 40k',
        'Carcassonne',          'Alhambra',             'Alien vs Predator',    'Card Kingdoms',
        'The Lord of the Rings','Core Rulebook',        'Bounty Hunters',       'Warhammer',
        'Triumph of Chaos',     'Pokémon',              'Digimon',              'Torg Eternity',
        'Munchkin',             'The Witcher',          'Viticulture: Tuscany', 'The Witcher: Old World',
        'Star Wars: Destiny',	'Anachrony',      		'Patchwork',            'BANG',
        'X-Wing',               'Y-Wing',               'A Máscara',            'Harry Potter',
        'Dwar7s',               'Marco Polo',           'Glen More',            'Disney',
        'Banco Imobiliário',    'Hanabi',               'Código Secreto',       'Codenames',
        'Pixel Tactics',        'Adventure Time'        
    }

    for serie in series:
        match = re.match(f'{serie}[\s][^:]', string)
        search = re.search(f'{serie}[\s][^:]', string)

        if match or search:
            string = string.replace(serie, f'{serie}: ')

    return string


def fix_editions(string):
    editions = [
        'DeluxeEdition',
        'SpecialEdition'
    ]

    tag_exceptions = [
        ' ', '#'
    ]

    for edition in editions:
        index = string.find(edition)

        try:
            if index > 0:
                if string[index-1] not in tag_exceptions:
                    string = string.replace(edition, f' #{edition}')

        except IndexError:
            pass

    return string


def remove_single_hashtag(string):
    patterns = [
        '\s+#$', '\s+#\s+'
    ]

    for pattern in patterns:
        single_hashtag = re.compile(pattern)
        string = re.sub(single_hashtag, ' ', string)

    return string


def remove_redundant_tags(string):
    redundant_tags = [
        '#TheBoardGame',
        '#ADeckBuildingAdventure'
    ]

    for tag in redundant_tags:
        string = string.replace(tag, '')

    return string


def fix_hashtags(string):
    patterns = [
        '#[0-9]*[Ee]dição[\w]*\s*',
        '[0-9]{1,}[stndrdth]{2,}[Ee]dition[\w]*\s*',
        '[0-9]{1,}[Ee]dition[\w]*\s*',
        'DeckBuildingGame',
        '[Vv]ol[0-9]',
        '#Expansão',
        '#Expansion',
    ]

    for pattern in patterns:
        string = re.sub(pattern, ' ', string, flags=re.IGNORECASE).rstrip()

    rpg_index = string.find('RPG')

    try:
        if rpg_index > 0:
            if string[rpg_index-1] != '#':
                string = string.replace('RPG', ' #RPG')

    except IndexError:
        pass

    return string


def remove_roman_hashtags(string):
    pattern = re.compile("([XVI]+)[XVI*]")

    search = re.search(pattern, string)

    if search != None:
        string = string[:search.start()] + " " + search.group()

    return string


def manage_exceptions(string):
    exceptions = {
        '#ManoplaDoInfinito #UmJogoLoveLetter': '#ManoplaDoInfinito Um Jogo #LoveLetter',
        '#Mission #RedPlanet': '#MissionRedPlanet'
    }

    if string in exceptions.keys():
        string = exceptions[string]

    return string


def generate_tag(game):
    tag = remove_special_chars(game)
    tag = replace_numbers(tag)
    tag = remove_patterns(tag)
    tag = manage_series(tag)
    tag = process_special_chars(tag)
    tag = merge_hyphens(tag)
    tag = split_into_tags(tag)
    tag = remove_redundant_tags(tag)
    tag = fix_hashtags(tag)
    tag = fix_editions(tag)
    tag = remove_roman_hashtags(tag)
    tag = remove_single_hashtag(tag)
    tag = manage_exceptions(tag)
    tag = tag.strip()

    return tag
