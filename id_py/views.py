from django.http import HttpResponse, HttpRequest
from django.template import loader
from io import TextIOWrapper
from .models import Token, Quote, Request
from .logic.vwrequest import TokenReceiver, PropertyGetter, TokenTester
from .logic.consts import HtmlConsts, UrlConsts
from .config import Config
from .logic.commissionnumber import CommissionNumber
from .logic.lock import LockDetector, Lock


# root/index page
def root(request: HttpRequest):
    template = loader.get_template('root.html')
    return HttpResponse(template.render({
        'please_enter': HtmlConsts.PLEASE_ENTER_COMM_NO,
        'url_consts': UrlConsts()
        }))


# the number endpoint /<number>
# example: /AF1234
def number(request: HttpRequest, number: str):

    try:
        commission_number = CommissionNumber(number)
    except CommissionNumber.CommissionNumberError:
        return HttpResponse('Malformed commission number.')

    lock: Lock = LockDetector().detect_lock(commission_number)
    if lock != None:
        template = loader.get_template('locked.html')
        return HttpResponse(
            template.render({
                'message': lock.message,
                'faq_url': UrlConsts.FAQ_URL
            })
        )

    if Config.request_logging_enabled:
        Request.persist(commission_number)

    # load the html template
    template = loader.get_template('number_template.html')

    # get the youngest token from the db
    token = Token.get_last()

    # if token is invalid, create a new one
    if token == None or TokenTester(token).test() == False:
        token: Token = TokenReceiver().main()
        token.save()

    # load properties
    properties = PropertyGetter(token, commission_number)
    properties.load()

    # obtain whether there are specs
    # background: for some numbers the specs are no specs available, this workaround avoids a NPE
    are_there_specs: bool = properties.details.get('specifications') != None

    # generate what to show
    show = properties.show()

    # generate a random quote
    random_quote = Quote.random_quote()

    spec_config = []

    try:
        spec_config_file: TextIOWrapper = open(Config.SPEC_CONFIG_LOCATION, 'r')
        spec_config_non_filtered: list[str] = spec_config_file.read().split('\n')
        spec_config = filter(lambda x: x != '' and x != None, spec_config_non_filtered)
        spec_config_file.close()
    except FileNotFoundError:
        pass

    selected_specs_non_filtered: list = map(properties.extract_from_specs, spec_config)
    selected_specs = filter(lambda x: x != None, selected_specs_non_filtered)

    # define template context
    context = { 'show': show, 
                'quote': random_quote if random_quote != None else HtmlConsts.NO_QUOTE_FOUND, 
                'consts': HtmlConsts(),
                'url_consts': UrlConsts(),
                'car': properties.data.get('modelName'),
                'color': properties.details.get('exteriorColorText'),
                'engine': properties.details.get('engine'),
                'model_year': properties.details.get('modelYear'),
                'specifications_present': are_there_specs,
                'selected_specs': selected_specs,
                }

    # create and return response
    return HttpResponse(
        template.render(context)
    )


# concise endpoint /<number>/concise
# returns True of vin present, False otherwise
def number_concise(request: HttpRequest, number: str):
    try:
        commission_number = CommissionNumber(number)
    except CommissionNumber.CommissionNumberError:
        return HttpResponse('Malformed commission number.')

    lock: Lock = LockDetector().detect_lock(commission_number)
    if lock != None:
        template = loader.get_template('locked.html')
        return HttpResponse(
            template.render({
                'message': lock.message,
                'faq_url': UrlConsts.FAQ_URL
            })
        )

    if Config.request_logging_enabled:
        Request.persist(commission_number)

    # get the youngest token from the db
    token = Token.get_last()

    # if token is invalid, create a new one
    if token == None or TokenTester(token).test() == False:
        token: Token = TokenReceiver().main()
        token.save()

    # load properties
    properties = PropertyGetter(token, commission_number)
    properties.load()

    # create and return response
    return HttpResponse(
        str(properties.data.get('vin') != None)
    )