__MAJOR__ = 0
__MINOR__ = 1
__MICRO__ = 0
__VERSION__ = (__MAJOR__, __MINOR__, __MICRO__)
__version__ = ','.join(str(n) for n in __VERSION__)


from apsjournals.journals import PRL, PRM, PRA, PRB, PRC, PRD, PRE, PRX, PRAB, PRApplied, PRFluids, PRMaterials, PRPER
