from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, TextAreaField, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length


STATES = [
    ('AC'), ('AL'), ('AP'), ('AM'), ('BA'),
    ('CE'), ('DF'), ('ES'), ('GO'), ('MA'),
    ('MT'), ('MS'), ('MG'), ('PA'), ('PB'),
    ('PE'), ('PR'), ('PI'), ('RJ'), ('RN'),
    ('RS'), ('RO'), ('RR'), ('SC'), ('SP'),
    ('SE'), ('TO'),
]

OFFER = [
    ('Apenas Venda'), ('Apenas Troca'), ('Venda ou Troca'), ('Leilão Externo'), ('Procura')
]


class BoardGameItemForm(FlaskForm):
    offer       = SelectField('Tipo', choices=OFFER)
    boardgame   = StringField('Nome', validators=[InputRequired()])
    details     = StringField('Detalhes sobre o item', validators=[Length(max=80)])
    price       = StringField('Preço', validators=[Length(max=8)])


class BoardGameForm(FlaskForm):
    boardgames          = FieldList(FormField(BoardGameItemForm),
                           min_entries=1, max_entries=50)
    city                = StringField('Cidade', validators=[InputRequired()])
    state               = SelectField('Estado', choices=STATES)
    general_details     = TextAreaField('Detalhes sobre o anúncio', render_kw={
                                    "rows": 4, "cols": 4}, validators=[Length(max=600)])
    boardgame_submit    = SubmitField('Enviar Anúncio')


class AuctionItemForm(FlaskForm):
    boardgame       = StringField('Nome', validators=[InputRequired()])
    details         = StringField('Detalhes sobre o item', validators=[Length(max=80)])
    starting_price  = StringField('Lance inicial', validators=[Length(max=8), InputRequired()])
    increment       = StringField('Incremento', validators=[Length(max=6), InputRequired()])


class AuctionForm(FlaskForm):
    boardgames      = FieldList(FormField(AuctionItemForm), min_entries=1, max_entries=50)
    city            = StringField('Cidade', validators=[InputRequired()])
    state           = SelectField('Estado', choices=STATES)
    ending_date     = StringField('Data', validators=[InputRequired()])
    ending_hour     = StringField('Horário', validators=[InputRequired()])
    general_details = TextAreaField('Detalhes sobre o anúncio', render_kw={
                                    "rows": 4, "cols": 4}, validators=[Length(max=600)])
    auction_submit  = SubmitField('Enviar Leilão')
