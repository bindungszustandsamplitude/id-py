
# class with static constants for html (text literals, ...)
class HtmlConsts:
    GOOD_NEWS = 'Hey, gute Nachrichten:'
    CHEERY_QUOTE = 'Hier ein aufmunternder Spruch:'
    NO_SPECS_AVAIL = 'Ausstattungsmerkmale nicht sichtbar.'
    SAD_MESSAGE = 'Leider nein, sorry :('
    DISCLAIMER = 'Aktuell funktioniert dieses Tool nur für Kommissionsnummern < AJ2728.'
    NO_CAR_FOUND = 'Leider kann zu dieser Kommissionsnummer kein Eintrag gefunden werden.'
    NO_QUOTE_FOUND = 'Leider sind noch keine Zitate in der Datenbank gespeichert.'

# class end

# class with static url constants
class UrlConsts:
    # login page
    ENTRY_POINT = \
    'https://www.volkswagen.de/app/authproxy' + \
    '/login?fag=vw-de,vw-de-online-sales,vwag-weconnect&scope-vw-de=profile,address,phone,carConfigurations' + \
    ',dealers,cars,vin,profession&scope-vw-de-online-sales=address,phone,profile&scope-vwag-weconnect=openid,' + \
    'mbb&prompt-vw-de-online-sales=none&prompt-vwag-weconnect=none&redirectUrl' + \
    '=https://www.volkswagen.de/de/besitzer-und-nutzer/myvolkswagen.html'

    # mail submission page
    LOGIN_FORM_MAIL_ENTRY_POINT = \
    'https://identity.vwgroup.io/signin-service/v1/' + \
    '4fb52a96-2ba3-4f99-a3fc-583bb197684b@apps_vw-dilab_com/login/identifier'
    
    # password submission page
    LOGIN_FORM_PASSWORD_ENTRY_POINT = \
    'https://identity.vwgroup.io/signin-service/v1/4fb52a96-2ba3-4f99-a3fc-583bb197684b@apps_vw-dilab_com/' + \
    'login/authenticate'
    
    # token api
    TOKEN_URL = 'https://www.volkswagen.de/app/authproxy/vw-de/tokens'

    # test url for token testing. the vin AF1234 definitely exists.
    TOKEN_TEST_URL = 'https://myvw-gvf-proxy.apps.emea.vwapps.io/vehicleData/de-DE/1852021AF1234'

#class end


# prefixes
class PrefixConsts:
    PREFIX_2022 = '1852022'
    PREFIX_2021 = '1852021'

# class end