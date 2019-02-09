__MAJOR__ = 0
__MINOR__ = 2
__MICRO__ = 0
__VERSION__ = (__MAJOR__, __MINOR__, __MICRO__)
__version__ = '.'.join(str(n) for n in __VERSION__)
__github_url__ = 'http://github.com/JWKennington/apsjournals'


from apsjournals.journals import PRL, PRM, PRA, PRB, PRC, PRD, PRE, PRX, PRAB, PRApplied, PRFluids, PRMaterials, PRPER
from apsjournals.web.auth import authenticate
