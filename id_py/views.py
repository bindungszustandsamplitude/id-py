from django.http import HttpResponse, HttpRequest
from django.template import loader
from .models import Token, Quote, Request
from .logic.vwrequest import TokenReceiver, PropertyGetter, TokenTester
from .logic.consts import HtmlConsts
from .config import Config
from .logic.commissionnumber import CommissionNumber


# the number endpoint /<number>
# example: /AF1234
def number(request: HttpRequest, number: str):

    try:
        commission_number = CommissionNumber(number)
    except CommissionNumber.CommissionNumberError:
        return HttpResponse('Malformed commission number.')

    if Config.request_logging_enabled:
        Request.persist(commission_number)

    # load the html template
    template = loader.get_template('number_template.html')

    # get the youngest token from the db
    token = Token.get_last()

    # if token is invalid, create a new one
    if TokenTester(token).test() == False:
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

    # define template context
    context = { 'show': show, 
                'quote': Quote.random_quote(), 
                'consts': HtmlConsts(),
                'car': properties.data.get('modelName'),
                'engine': properties.details.get('engine'),
                'model_year': properties.details.get('modelYear'),
                'specifications_present': are_there_specs,
                'software': properties.extract_from_specs('Softwareverbund'),
                'fertigungsablauf': properties.extract_from_specs('Fertigungsablauf')
                }
    
    # create and return response
    return HttpResponse(
        template.render(context)
    )


def number_concise(request: HttpRequest, number: str):
    try:
        commission_number = CommissionNumber(number)
    except CommissionNumber.CommissionNumberError:
        return HttpResponse('Malformed commission number.')

    if Config.request_logging_enabled:
        Request.persist(commission_number)

    # get the youngest token from the db
    token = Token.get_last()

    # if token is invalid, create a new one
    if TokenTester(token).test() == False:
        token: Token = TokenReceiver().main()
        token.save()
    
    # load properties
    properties = PropertyGetter(token, commission_number)
    properties.load()
    
    # create and return response
    return HttpResponse(
        str(properties.data.get('vin') != None)
    )