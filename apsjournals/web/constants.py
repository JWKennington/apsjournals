"""Constants related to website structure and endpoints
"""


import enum
import re
import string


class Url(str):
    def __init__(self, fmt: str):
        """A Url is a string that is aware of its parameters, and that can
        turn itself into a regex pattern (for parsing url parameters)
        
        Args:
            fmt: 
                str, the formatted string
        """
        super().__init__()
        self._format = fmt

    @property
    def parameters(self):
        return [i[1] for i in list(string.Formatter().parse(self._format)) if i[1] is not None]

    def format(self, **kwargs):
        """Format the string
        
        Args:
            kwargs:
                dict, keyword arguments. MUST specify ALL parameters otherwise will raise 

        Returns:
            str, the formatted URL string
        """
        kwargs = kwargs.copy()  # prevent changes to original kwargs
        params = self.parameters
        for n, p in enumerate(params):
            if p not in kwargs:
                raise ValueError('Missing parameter {} for URL {}'.format(p, self._format))
            if kwargs[p] is None:  # replace None with empty string
                if n < len(params) - 1:
                    raise ValueError('None value only permitted for final parameter {}, not {}'.format(params[-1], p))
                kwargs[p] = ''
        return self._format.format(**{p: kwargs[p] for p in params})

    def as_re(self, compile: bool=True):
        """Convert the URL to a regex pattern for parsing parameters from string urls

        Args:
            compile: 
                bool, if True then compile the pattern

        Returns:
            str or re.Pattern
        """
        pattern = self._format
        for p in self.parameters:
            pattern = pattern.replace('{{{}}}'.format(p), r'(?P<{}>\w*)'.format(p))
        if compile:
            pattern = re.compile(pattern)
        return pattern


class URL(str, enum.Enum):
    """URL constants"""
    Root = Url('https://journals.aps.org')


class URLParameter(str, enum.Enum):
    """URL Parameters standard across endpoints"""
    Journal = 'journal'
    Volume = 'volume'
    Issue = 'issue'


class EndPoint(Url, enum.Enum):
    """Formatted endpoints for specific api interface"""
    Volume = Url('{root}/{{{param_journal}}}/issues/{{{param_volume}}}'.format(root=URL.Root, 
                                                                               param_journal=URLParameter.Journal, 
                                                                               param_volume=URLParameter.Volume)) 
    Issue = Url('{root}/{{{param_journal}}}/issues/{{{param_volume}}}/{{{param_issue}}}'.format(root=URL.Root, 
                                                                                                param_journal=URLParameter.Journal, 
                                                                                                param_volume=URLParameter.Volume, 
                                                                                                param_issue=URLParameter.Issue))
