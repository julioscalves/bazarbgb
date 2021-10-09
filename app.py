import hashlib
import hashtag
import hmac
import json
import os
import re
import requests
import sqlite3
import urllib

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv
from forms import AuctionForm, AuctionItemForm, BoardGameForm, BoardGameItemForm
from flask import Flask, flash, render_template, redirect, jsonify, url_for
from flask.globals import request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
cors = CORS(app)

env_path = os.path.join(os.getcwd(), '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
USERS_DB_NAME = os.getenv('USERS_DB_NAME')
BGB_BAZAR_CHANNEL_ID = os.getenv('BGB_BAZAR_CHANNEL_ID')

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///names.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.init_app(app)

class Names(db.Model):
    __tablename__ = "boardgames"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)


def remove_non_number(string):
    """
    Removes non number related characters.

    Args:
        string ([str]): [uncleaned string]

    Returns:
        [str]: [cleaned string]
    """
    pattern = re.compile('[^0-9,.]')
    cleaned_string = re.sub(pattern, '', string)

    return cleaned_string


def assemble_message(adtype, text_list, output):
    """
    Assembles the output message

    Args:
        adtype ([str]): [type of message]
        text_list ([str]): [items]
        output ([str]): [output message]

    Returns:
        [str]: [output message]
    """
    if len(text_list) > 0:
        if adtype == 'Apenas Venda':
            output += '💵 #VENDO\n\n'

        elif adtype == 'Apenas Troca':
            if '#' in output:
                output += '\n'
            output += '🤝 #TROCO\n\n'

        elif adtype == 'Venda ou Troca':
            if '#' in output:
                output += '\n'
            output += '⚖️ #VENDO OU #TROCO\n\n'

        elif adtype == 'Leilão Externo':
            if '#' in output:
                output += '\n'
            output += '🔨 #LEILÃO\n\n'

        else:
            if '#' in output:
                output += '\n'
            output += '🔎 #PROCURO\n\n'

        for ad in text_list:
            output += f'{ad}\n'

    return output


def handle_data(data, int_keys):
    """
    Handles the unpacked form data into the output message
    and sends it to Telegram as a POST request.

    Args:
        data ([dict]): [unpacked form data]
        int_keys ([list]): [data indexes]
    """
    output = ''
    print(data)

    if data['message_type'] == 'boardgame':
        sell, trade, trade_or_sell, auction, search = [], [], [], [], []

        for index in int_keys:
            boardgame = data[index].get('boardgame')
            formatted_name = hashtag.generate_tag(boardgame)

            data[index]['name'] = formatted_name
            formatted_name = data[index]['name']
            offer = data[index]['offer']
            details = data[index]['details']

            if offer == 'Apenas Venda':
                price = remove_non_number(data[index]['price'])
                message = f'\t\t↳ {formatted_name} R$ {price}\n\t\t{details}'.rstrip(
                )
                sell.append(message)

            elif offer == 'Apenas Troca':
                message = f'\t\t↳ {formatted_name}\n\t\t{details}'.rstrip()
                trade.append(message)

            elif offer == 'Venda ou Troca':
                price = remove_non_number(data[index]['price'])
                message = f'\t\t↳ {formatted_name} R$ {price}\n\t\t{details}'.rstrip(
                )
                trade_or_sell.append(message)

            elif offer == 'Leilão Externo':
                message = f'\t\t↳ {formatted_name}\n\t\t{details}'.rstrip()
                auction.append(message)

            else:
                message = f'\t\t↳ {formatted_name}\n\t\t{details}'.rstrip()
                search.append(message)

        output += f'<strong>Anúncios de @{data.get("username")}</strong>' + '\n\n'

        for adtype, text_list in zip(['Apenas Venda', 'Apenas Troca', 'Venda ou Troca', 'Leilão Externo', 'Procura'], [sell, trade, trade_or_sell, auction, search]):
            output = assemble_message(adtype, text_list, output)

    else:
        username = data.get("username")
        ending_date = data.get('ending_date')
        ending_hour = data.get('ending_hour')

        output += f'<strong>Leilão de @{username}</strong>' + '\n\n'
        output += f'Encerramento: {format_date(ending_date)} às {ending_hour}h' + '\n\n'

        for index in int_keys:
            boardgame = data[index].get('boardgame')
            starting_price = format_price(data[index].get('starting_price'))
            increment = format_price(data[index].get('increment'))
            details = data[index].get('details').strip()
            formatted_name = hashtag.generate_tag(boardgame)

            if index > 1:
                output += f'\nJogo: #{format_index(index)} {formatted_name}\n'

            else:
                output += f'Jogo: #{format_index(index)} {formatted_name}\n'

            output += f'Lance inicial: R$ {starting_price}.\n'
            output += f'Incremento: R$ {increment}.\n'

            if len(details) > 0:
                output += f'Detalhes: {details}\n'

    city = data['city'].title().replace('-', '').replace(' ', '').replace("'", '')
    state = data['state']

    general_details = data['general_details'].strip()

    if len(general_details) > 0:
        output += f'\n{general_details}\n\n'
        output += f'📌 #{city} #{state}'

    else:
        output += f'\n📌 #{city} #{state}'

    output = urllib.parse.quote_plus(output)

    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={BGB_BAZAR_CHANNEL_ID}&text={output}&parse_mode=HTML'
    requests.post(url)


def format_date(date):
    """
    Reformats the date from the form.

    Args:
        date ([str]): [date]

    Returns:
        [str]: [reformated date]
    """
    date = date.split('-')
    day, month, year = date[-1], date[-2], date[-3]

    return f'{day}/{month}/{year}'


def format_index(index):
    """
    Reformats the index into a string

    Args:
        index ([int]): [index]

    Returns:
        [str]: [index]
    """
    if index < 10:
        return f'0{index}'


def format_price(price):
    """
    Formats the price from the form data

    Args:
        price ([float]): [price data]

    Returns:
        [str]: [price string]
    """
    if '.' in price or ',' in price:
        price = price.replace('.', ',')

        if len(price.split(',')[-1]) == 1:
            price += '0'

    return price


def check_user(telegram_data):
    """
    Verifies if the user is registered into the database

    Args:
        telegram_data ([dict]): [telegram auth data]

    Returns:
        [bool or db_query]: [if the user is not registered, returns false.
                             otherwise, returns the db query.]
    """
    con = sqlite3.connect(USERS_DB_NAME)
    cur = con.cursor()

    db_user = cur.execute(f'SELECT * FROM users WHERE id={telegram_data["id"]}').fetchone()

    con.commit()
    con.close()

    if db_user is None:
        return False

    else:
        return db_user


def unpack_data(form_data, telegram_data, data_source):
    """
    Unpacks the form data into a dictionary

    Args:
        form_data ([dict]): [unpacked form data]
        telegram_data ([dict]): [telegram auth data]
        data_source ([str]): [if the data is from an auction or standard boardgame]

    Returns:
        [dict]: [unpacked data]
        [list]: [index numbers]
    """
    con = sqlite3.connect(USERS_DB_NAME)
    cur = con.cursor()

    db_user = check_user(telegram_data)

    future_date = datetime.now() + timedelta(hours=168) - timedelta(hours=3)

    if db_user is False:
        cur.execute('INSERT INTO users VALUES (:id, :username, :is_banned, :block_until)', {
                        'id'            : telegram_data['id'],
                        'username'      : telegram_data['username'],
                        'is_banned'     : 0,
                        'block_until'   : future_date,
                    })

    else:
        cur.execute('UPDATE users SET block_until = :block_until WHERE id = :id', {
                        'block_until'   : future_date,
                        'id'            : telegram_data['id'],
                    })

    con.commit()
    con.close()

    data = {}

    data['city']            = form_data.city.data
    data['state']           = form_data.state.data
    data['general_details'] = form_data.general_details.data
    data['username']        = telegram_data['username']
    data['userid']          = telegram_data['id']

    if data_source == 'auction':
        data['ending_date']     = form_data.ending_date.data
        data['ending_hour']     = form_data.ending_hour.data
        data['message_type']    = 'auction'

    else:
        data['message_type'] = 'boardgame'

    index = 1

    for games in form_data.boardgames.data:
        if data_source == 'auction':
            data[index] = {
                'boardgame'     : games['boardgame'],
                'starting_price': games['starting_price'],
                'increment'     : games['increment'],
                'name'          : '',
                'details'       : games['details'],
            }

        else:
            data[index] = {
                'boardgame' : games['boardgame'],
                'offer'     : games['offer'],
                'name'      : '',
                'price'     : format_price(games['price']),
                'details'   : games['details'],
            }

        index += 1

    int_keys = list(filter(lambda i: type(i) == int, data.keys()))

    return data, int_keys


def authenticate(telegram_data):
    """
    Authenticates telegram's auth data

    Args:
        telegram_data ([dict]): [telegram's auth data]

    Returns:
        [bool]: [current user authentication status]
    """
    day_auth_time = 86_400
    auth_data = telegram_data.copy()
    auth_hash = auth_data['hash']
    auth_data.pop('hash', None)

    if auth_data['photo_url'] == None:
        auth_data.pop('photo_url', None)

    auth_data_keys = sorted(auth_data.keys())
    data_check_string = []

    for key in auth_data_keys:
        if auth_data[key] != None:
            data_check_string.append(key + '=' + auth_data[key])

    data_check_string = '\n'.join(data_check_string)

    token_secret_key = hashlib.sha256(TELEGRAM_TOKEN.encode()).digest()
    hmac_hash = hmac.new(token_secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

    auth_date = datetime.fromtimestamp(int(auth_data['auth_date']))
    now = datetime.now()

    auth_delta = now - auth_date

    if hmac_hash != auth_hash:
        return False

    elif auth_delta.seconds > day_auth_time:
        return False

    else:
        return True


def bgg_query(game):
    """
    BGG's query.

    Args:
        game ([str]): [boardgame name]

    Returns:
        [str]: [request's response text]
    """
    url = f'https://www.boardgamegeek.com/xmlapi/search?search={game}'
    request = requests.get(url)

    return request.text


def search_bgg(name):
    """
    Send a query to BGG.

    Args:
        name ([str]): [boardgame name]

    Returns:
        [list]: [boardgame names]
    """

    bgg_response = bgg_query(name)
    soup = BeautifulSoup(bgg_response, 'lxml')

    games = []

    for game in soup.find_all('name', attrs={'primary': 'true'})[:10]:
        games.append(game.text)

    return games


def format_cj_name(name):
    """
    Formats the query name to the comparajogos' request

    Args:
        name ([str]): [preformat name]

    Returns:
        [str]: [formatted name]
    """
    try:
        special_chars = ['-', ':', '.', ',']

        for char in special_chars:
            name.replace(char, '%')

        name = f'%{name}%'.lower().replace(' ', '%')

        return name

    except AttributeError:
        return ""


def search_comparajogos(name):
    """
    Comparajogos' query.

    Args:
        name ([str]): [boardgame name]

    Returns:
        [list]: [boardgames names]
    """
    name = format_cj_name(name)
    url = 'https://btr620i3rc.execute-api.sa-east-1.amazonaws.com/'
    query = f'{{ product(where: {{name: {{_ilike: "{name}"}}}}) {{ name }} }}'

    response = requests.post(url, json={'query': query})
    json_data = json.loads(response.text)

    results = [data['name'] for data in json_data['data']['product']]

    return results


@app.route('/bgsearch')
@cross_origin()
def bgsearch():
    """
    Receives the AJAX queries from the frontend

    Returns:
        [json]: [boardgames]
    """
    name = request.args.get('bgquery')

    dbquery = Names.query.filter(Names.name.ilike(f'%{name}%')).all()
    results = [result.name for result in dbquery][:20]

    if len(results) < 5:
        bgg = search_bgg(name)
        results = list(set([*results, *bgg]))

    results.sort()
    results = results[:20]    

    return jsonify(bglist=results)


@app.route('/faq')
def faq():
    """
    Renders FAQ's page.

    Returns:
        [function]: [faq's page]
    """
    return render_template('faq.html')


@app.route("/", methods=['GET', 'POST'])
def home():
    """
    Renders and controls the home page.

    Returns:
        [function]: [renders the homepage, either directly or through redirects]
    """
    auction_form = AuctionForm()
    boardgame_form = BoardGameForm()

    auction_template_form = AuctionItemForm(prefix='boardgames-_-')
    boardgame_template_form = BoardGameItemForm(prefix='boardgames-_-')

    telegram_auth = False

    telegram_data = {
        'id'        : request.args.get('id', None),
        'first_name': request.args.get('first_name', None),
        'last_name' : request.args.get('last_name', None),
        'username'  : request.args.get('username', None),
        'auth_date' : request.args.get('auth_date', None),
        'hash'      : request.args.get('hash', None),
        'photo_url' : request.args.get('photo_url', None)
    }

    if telegram_data['id'] != None:
        
        if telegram_data['username'] == None:
            flash('Por favor, defina um nome de usuário no Telegram antes de utilizar este site.')
            return redirect(url_for('home'))

        if authenticate(telegram_data):
            db_user = check_user(telegram_data)

            if db_user is False:
                telegram_auth = True

            else:
                is_banned = db_user[2]
                block_until = datetime.strptime(db_user[3], '%Y-%m-%d  %H:%M:%S.%f')
                timenow = datetime.now() - timedelta(hours=3)

                if is_banned == 0 and block_until < timenow:
                    telegram_auth = True

                elif is_banned == 1:
                    flash('Este usuário está banido do BGB Bazar e, por isso, não pode enviar mensagens.')

                elif block_until > timenow:
                    flash(f'Você só poderá enviar uma nova mensagem após {block_until.strftime("%d/%m às %H:%Mh")}.')
        
        else:
            flash('Falha de autenticação. Por favor, tente realizar o login novamente.')

    if request.method == 'POST':
        is_auction_submitted = auction_form.data.get('auction_submit')
        is_boardgame_submitted = boardgame_form.data.get('boardgame_submit')

        if auction_form.validate() and is_auction_submitted:
            ads, int_keys = unpack_data(
                auction_form, telegram_data, data_source='auction')
            handle_data(ads, int_keys)

            return redirect(url_for('home', success='true'))

        elif boardgame_form.validate() and is_boardgame_submitted:
            ads, int_keys = unpack_data(
                boardgame_form, telegram_data, data_source='boardgame')
            handle_data(ads, int_keys)

            return redirect(url_for('home', success='true'))

    return render_template('home.html', telegram_auth=telegram_auth, boardgame_form=boardgame_form, auction_form=auction_form, _boardgame_template_form=boardgame_template_form, _auction_template_form=auction_template_form)


if __name__ == '__main__':
    app.run(debug=False)
