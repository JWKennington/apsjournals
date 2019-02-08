"""Authentication utilities
"""


from apsjournals.web.constants import EndPoint
import requests
import scrapy


# Note that the authenticity token xpath constant below is dependent on the aps website
# structure, and will consequently need to be maintained in order to obtain the authenticity token,
# which is the necessary first step to getting the full auth token
_AUTHENTICITY_TOKEN_XPATH = '//form[@action="/login"]/input[@name="authenticity_token"]/@value'
_AUTH_TOKEN_COOKIE_NAME = 'auth_token'
_RACK_SESSION_COOKIE_NAME = 'rack.session'

# The two constants below are session-level global constants used for tracking the required
# cookies for completing the authentication process. Do NOT change them manually, or the
# authentication will be invalidated
_AUTH_TOKEN = None
_RACK_SESSION = None

# The headers below are created on 2019-01-20 and are tested against
# current versions of chrome and the aps website
_LOGIN_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '143',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'journals.aps.org',
    'Origin': 'https://journals.aps.org',
    'Referer': 'https://journals.apr.org/login',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}


class AuthenticationError(ValueError):
    """A specific error class for authentication utilities"""
    pass


def cookies():
    """Helper function for computing the auth cookies"""
    if _AUTH_TOKEN is None or _RACK_SESSION is None:
        raise AuthenticationError('Must authenticate before requesting data. See apsjournals.authenticate.')
    return {
        _AUTH_TOKEN_COOKIE_NAME: _AUTH_TOKEN,
        _RACK_SESSION_COOKIE_NAME: _RACK_SESSION,
    }


def authenticate(username: str=None, password: str=None):
    """Authentication for APS website

    Args:
        username: 
            str, the APS username
        password: 
            str, the APS password

    Returns:
        None, but sets the value of module level constants 
        _AUTH_TOKEN, _RACK_SESSION
    """
    if username is None:
        username = input('Username: ')
    if password is None:
        password = input('Password: ')

    # declare the globals to set the state of the session
    global _AUTH_TOKEN, _RACK_SESSION

    # Get initial login page so we can extract the authenticity token and the rack session
    pre_login_response = requests.get(EndPoint.Login.format())
    sel = scrapy.Selector(text=pre_login_response.content)
    authenticity_token = sel.xpath(_AUTHENTICITY_TOKEN_XPATH)
    _RACK_SESSION = pre_login_response.cookies[_RACK_SESSION_COOKIE_NAME]

    # submit login form with credentials
    response = requests.post(EndPoint.Login.format(), allow_redirects=False, headers=_LOGIN_HEADERS,
                             cookies={_RACK_SESSION_COOKIE_NAME: _RACK_SESSION},
                             data={
                                 '_method': 'put',
                                 'authenticity_token': authenticity_token,
                                 'username': username,
                                 'password': password,
                             })

    if not response.status_code == 302:
        raise AuthenticationError('Authentication form failed with error: {}'.format(response.reason))
    _AUTH_TOKEN = response.cookies[_AUTH_TOKEN_COOKIE_NAME]
