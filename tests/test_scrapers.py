import datetime
import functools
import mock
import pathlib
import unittest
from apsjournals.web import scrapers
from apsjournals.web.constants import EndPoint


STATIC_DIR = pathlib.Path(__file__).parent / 'static' 


def get_params_from_url(url: str, ep: EndPoint) -> tuple:
    m = ep.as_re().match(url)
    if m is not None:
        return m.groups()
    raise ValueError('Unable to match url against known endpoints: {}'.format(url))


def get_aps_static(url: str, ep: EndPoint):
    params = get_params_from_url(url, ep)
    if len(params) == 2: # missing issue
        params = params + (None,)
    journal, volume, issue = params
    file_name = str(volume) + ('' if issue is None else '-' + str(issue)) + '.htm'
    p = STATIC_DIR / journal / file_name
    with open(p.as_posix()) as fid:
        return fid.read()


class StaticTests(unittest.TestCase):
    def test_get_params_from_url(self):
        url = EndPoint.Volume.format(journal='prl', volume=121)
        self.assertEqual(get_params_from_url(url, EndPoint.Volume), ('prl', '121'))

    def test_get_aps_static(self):
        url = EndPoint.Volume.format(journal='prl', volume=121)
        source = get_aps_static(url, EndPoint.Volume)
        self.assertEqual(source[:20], "<!DOCTYPE html>\n<!--")

    def test_get_aps_static_issue(self):
        url = EndPoint.Issue.format(journal='prl', volume=121, issue=6)
        source = get_aps_static(url, EndPoint.Issue)
        self.assertEqual(source[:20], "<!DOCTYPE html>\n<!--")


class ScraperTests(unittest.TestCase):
    def test_base_scraper(self):
        s = scrapers.Scraper(endpoint=EndPoint.Volume)
        source = s.get(journal='prl', volume=121)
        self.assertEqual(source[:30].decode(), "<!DOCTYPE html><!--[if IE 8]><")

    def test_volume_index_scraper(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            s = scrapers.VolumeIndexScraper()
            info = s.load(journal='prl', volume=None)
            self.assertEqual(info[10],
                             scrapers.VolumeInfo(url='https://journals.aps.org/prl/issues/112',
                                                 num=112, start=datetime.date(2014, 1, 1),
                                                 end=datetime.date(2014, 3, 1)))

            info = s.load(journal='prl', volume=121)
            self.assertEqual(info[10],
                             scrapers.VolumeInfo(url='https://journals.aps.org/prl/issues/112',
                                                 num=112, start=datetime.date(2014, 1, 1),
                                                 end=datetime.date(2014, 3, 1)))

    def test_issue_index_scraper(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Volume)):
            s = scrapers.IssueIndexScraper()
            info = s.load(journal='prl', volume=121, issue=6)
            self.assertEqual(info[0], scrapers.IssueInfo(url='https://journals.aps.org/prl/issues/121/1', num=1, label=' 6 July 2018 (010401 — 019901)'))

    def test_issue_scraper(self):
        with mock.patch('apsjournals.web.scrapers.get_aps', side_effect=functools.partial(get_aps_static, ep=EndPoint.Issue)):
            s = scrapers.IssueScraper()
            info = s.load(journal='prl', volume=121, issue=6)
            expected = [scrapers.DividerInfo(name='HIGHLIGHTED ARTICLES'), 
                        scrapers.ArticleInfo(name='Magnetic Levitation Stabilized by Streaming Fluid Flows', author='K.\u2009A. Baldwin, J.-B. de Fouchier, P.\u2009S. Atkinson, R.\u2009J.\u2009A. Hill, M.\u2009R. Swift, and D.\u2009J. Fairhurst', teaser='Researchers have identified a regime under which a magnetic stir bar can be made to levitate while it spins in a fluid.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064502', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064502'), 
                        scrapers.ArticleInfo(name='First Six Dimensional Phase Space Measurement of an Accelerator Beam', author='Brandon Cathey, Sarah Cousineau, Alexander Aleksandrov, and Alexander Zhukov', teaser='A new technique provides the first measurement of all six characteristics of a particle beam, which will help researchers improve beam quality.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064804', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064804'), 
                        scrapers.ArticleInfo(name='Ubiquitous Spin-Orbit Coupling in a Screw Dislocation with High Spin Coherency', author='Lin Hu, Huaqing Huang, Zhengfei Wang, W. Jiang, Xiaojuan Ni, Yinong Zhou, V. Zielasek, M.\u2009G. Lagally, Bing Huang, and Feng Liu', teaser='Dislocation defects are often a nuisance in semiconductors, but theoretical work shows they might offer an improved route to producing spin currents.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066401', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066401'), 
                        scrapers.ArticleInfo(name='Black Hole Quasibound States from a Draining Bathtub Vortex Flow', author='Sam Patrick, Antonin Coutant, Maurício Richartz, and Silke Weinfurtner', teaser='A proposal to study quasi-bound states of rotating black holes makes use of the background vorticity in a draining bathtub.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061101', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061101'), 
                        scrapers.ArticleInfo(name='Elastic Purcell Effect', author='Mikołaj K. Schmidt, L.\u2009G. Helt, Christopher G. Poulton, and M.\u2009J. Steel', teaser='A mechanical analogue to the Purcell effect is proposed, for which elastic radiation from a localized emitter is modified by generic resonant microantennas.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064301', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064301'), 
                        scrapers.ArticleInfo(name='Van der Waals Spin Valves', author='C. Cardoso, D. Soriano, N.\u2009A. García-Martínez, and J. Fernández-Rossier', teaser='A new spin valve design consists of stacked van der Waals layers of graphene and ferromagnetic insulators.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067701', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067701'), 
                        scrapers.DividerInfo(name='LETTERS'), 
                        scrapers.SectionInfo(name='General Physics: Statistical and Quantum Mechanics, Quantum Information, etc.', articles=[
                            scrapers.ArticleInfo(name='Coulomb-Gas Electrostatics Controls Large Fluctuations of the Kardar-Parisi-Zhang Equation', author='Ivan Corwin, Promit Ghosal, Alexandre Krajenbrink, Pierre Le Doussal, and Li-Cheng Tsai', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060201', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060201'), 
                            scrapers.ArticleInfo(name='Controllable Non-Markovianity for a Spin Qubit in Diamond', author='J.\u2009F. Haase, P.\u2009J. Vetter, T. Unden, A. Smirne, J. Rosskopf, B. Naydenov, A. Stacey, F. Jelezko, M.\u2009B. Plenio, and S.\u2009F. Huelga', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060401', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060401'), 
                            scrapers.ArticleInfo(name='Twins Percolation for Qubit Losses in Topological Color Codes', author='Davide Vodola, David Amaro, Miguel Angel Martin-Delgado, and Markus Müller', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060501', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060501'), 
                            scrapers.ArticleInfo(name='Fast and Unconditional All-Microwave Reset of a Superconducting Qubit', author='P. Magnard, P. Kurpiers, B. Royer, T. Walter, J.-C. Besse, S. Gasparinetti, M. Pechal, J. Heinsoo, S. Storz, A. Blais, and A. Wallraff', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060502', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060502'), 
                            scrapers.ArticleInfo(name='Parity-Engineered Light-Matter Interaction', author='J. Goetz, F. Deppe, K.\u2009G. Fedorov, P. Eder, M. Fischer, S. Pogorzalek, E. Xie, A. Marx, and R. Gross', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060503', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060503'), 
                            scrapers.ArticleInfo(name='Internal Entanglement and External Correlations of Any Form Limit Each Other', author='S. Camalet', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060504', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060504'), 
                            scrapers.ArticleInfo(name='Quantum Schur Sampling Circuits can be Strongly Simulated', author='Vojtěch Havlíček and Sergii Strelchuk', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060505', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060505'), 
                            scrapers.ArticleInfo(name='Achieving Heisenberg-Scaling Precision with Projective Measurement on Single Photons', author='Geng Chen, Lijian Zhang, Wen-Hao Zhang, Xing-Xiang Peng, Liang Xu, Zhao-Di Liu, Xiao-Ye Xu, Jian-Shun Tang, Yong-Nan Sun, De-Yong He, Jin-Shi Xu, Zong-Quan Zhou, Chuan-Feng Li, and Guang-Can Guo', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060506', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060506'), 
                            scrapers.ArticleInfo(name='Spectral Statistics in Spatially Extended Chaotic Quantum Many-Body Systems', author='Amos Chan, Andrea De Luca, and J.\u2009T. Chalker', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.060601', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.060601')]), 
                        scrapers.SectionInfo(name='Gravitation and Astrophysics', articles=[
                            scrapers.ArticleInfo(name='Black Hole Quasibound States from a Draining Bathtub Vortex Flow', author='Sam Patrick, Antonin Coutant, Maurício Richartz, and Silke Weinfurtner', teaser='A proposal to study quasi-bound states of rotating black holes makes use of the background vorticity in a draining bathtub.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061101', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061101'), 
                            scrapers.ArticleInfo(name='Searching for Dark Photon Dark Matter with Gravitational-Wave Detectors', author='Aaron Pierce, Keith Riles, and Yue Zhao', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061102', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061102')]), 
                        scrapers.SectionInfo(name='Elementary Particles and Fields', articles=[
                            scrapers.ArticleInfo(name='Braiding with Borromean Rings in (', author='AtMa P.\u2009O. Chan, Peng Ye, and Shinsei Ryu', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061601', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061601'), 
                            scrapers.ArticleInfo(name='Testing Dark Decays of Baryons in Neutron Stars', author='Gordon Baym, D.\u2009H. Beck, Peter Geltenbort, and Jessie Shelton', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061801', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061801'), 
                            scrapers.ArticleInfo(name='Neutron Stars Exclude Light Dark Baryons', author='David McKeen, Ann E. Nelson, Sanjay Reddy, and Dake Zhou', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061802', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061802'), 
                            scrapers.ArticleInfo(name='SENSEI: First Direct-Detection Constraints on Sub-GeV Dark Matter from a Surface Run', author='Michael Crisler, Rouven Essig, Juan Estrada, Guillermo Fernandez, Javier Tiffenberg, Miguel Sofo Haro, Tomer Volansky, and Tien-Tien Yu (SENSEI Collaboration)', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.061803', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.061803'), 
                            scrapers.ArticleInfo(name='Observation of ', author='E. Guido ', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.062001', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.062001'), 
                            scrapers.ArticleInfo(name='Constraining Gluon Distributions in Nuclei Using Dijets in Proton-Proton and Proton-Lead Collisions at ', author='A.\u2009M. Sirunyan ', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.062002', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.062002'), 
                            scrapers.ArticleInfo(name='Measurement of the Absolute Branching Fraction of the Inclusive Decay ', author='M. Ablikim ', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.062003', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.062003')]), 
                        scrapers.SectionInfo(name='Nuclear Physics', articles=[
                            scrapers.ArticleInfo(name='Novel Shape Evolution in Sn Isotopes from Magic Numbers 50 to 82', author='Tomoaki Togashi, Yusuke Tsunoda, Takaharu Otsuka, Noritaka Shimizu, and Michio Honma', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.062501', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.062501'), 
                            scrapers.ArticleInfo(name='Neutron Star Tidal Deformabilities Constrained by Nuclear Theory and Experiment', author='Yeunhwan Lim and Jeremy W. Holt', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.062701', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.062701')]), 
                        scrapers.SectionInfo(name='Atomic, Molecular, and Optical Physics', articles=[
                            scrapers.ArticleInfo(name='Ultracold Rare-Earth Magnetic Atoms with an Electric Dipole Moment', author='Maxence Lepers, Hui Li, Jean-François Wyart, Goulven Quéméner, and Olivier Dulieu', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063201', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063201'), 
                            scrapers.ArticleInfo(name='Low-Energy Electron Emission in the Strong-Field Ionization of Rare Gas Clusters', author='Bernd Schütte, Christian Peltz, Dane R. Austin, Christian Strüber, Peng Ye, Arnaud Rouzée, Marc J.\u2009J. Vrakking, Nikolay Golubev, Alexander I. Kuleff, Thomas Fennel, and Jon P. Marangos', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063202', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063202'), 
                            scrapers.ArticleInfo(name='Quantum Synchronization and Entanglement Generation', author='Alexandre Roulet and Christoph Bruder', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063601', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063601'), 
                            scrapers.ArticleInfo(name='Sensing Static Forces with Free-Falling Nanoparticles', author='Erik Hebestreit, Martin Frimmer, René Reimann, and Lukas Novotny', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063602', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063602')]), 
                        scrapers.SectionInfo(name='Nonlinear Dynamics, Fluid Dynamics, Classical Optics, etc.', articles=[
                            scrapers.ArticleInfo(name='Precise Localization of Multiple Noncooperative Objects in a Disordered Cavity by Wave Front Shaping', author='Philipp del Hougne, Mohammadreza F. Imani, Mathias Fink, David R. Smith, and Geoffroy Lerosey', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063901', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063901'), 
                            scrapers.ArticleInfo(name='Thermal and Nonlinear Dissipative-Soliton Dynamics in Kerr-Microresonator Frequency Combs', author='Jordan R. Stone, Travis C. Briles, Tara E. Drake, Daryl T. Spencer, David R. Carlson, Scott A. Diddams, and Scott B. Papp', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063902', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063902'), 
                            scrapers.ArticleInfo(name='Measurements of Radiation Pressure Owing to the Grating Momentum', author='Ying-Ju Lucy Chu, Eric M. Jansson, and Grover A. Swartzlander, Jr.', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.063903', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.063903'), 
                            scrapers.ArticleInfo(name='Elastic Purcell Effect', author='Mikołaj K. Schmidt, L.\u2009G. Helt, Christopher G. Poulton, and M.\u2009J. Steel', teaser='A mechanical analogue to the Purcell effect is proposed, for which elastic radiation from a localized emitter is modified by generic resonant microantennas.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064301', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064301'), 
                            scrapers.ArticleInfo(name='Chaotic Blowup in the 3D Incompressible Euler Equations on a Logarithmic Lattice', author='Ciro S. Campolina and Alexei A. Mailybaev', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064501', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064501'), 
                            scrapers.ArticleInfo(name='Magnetic Levitation Stabilized by Streaming Fluid Flows', author='K.\u2009A. Baldwin, J.-B. de Fouchier, P.\u2009S. Atkinson, R.\u2009J.\u2009A. Hill, M.\u2009R. Swift, and D.\u2009J. Fairhurst', teaser='Researchers have identified a regime under which a magnetic stir bar can be made to levitate while it spins in a fluid.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064502', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064502'), 
                            scrapers.ArticleInfo(name='Transient Nonlinear Response of Dynamically Decoupled Ionic Conductors', author='Felix Wieland, Alexei\u2009P. Sokolov, Roland Böhmer, and Catalin Gainaru', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064503', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064503')]), 
                        scrapers.SectionInfo(name='Plasma and Beam Physics', articles=[
                            scrapers.ArticleInfo(name='Observation of High Transformer Ratio Plasma Wakefield Acceleration', author='Gregor Loisch, Galina Asova, Prach Boonpornprasert, Reinhard Brinkmann, Ye Chen, Johannes Engel, James Good, Matthias Gross, Florian Grüner, Holger Huck, Davit Kalantaryan, Mikhail Krasilnikov, Osip Lishilin, Alberto Martinez de la Ossa, Timon J. Mehrling, David Melkumyan, Anne Oppelt, Jens Osterhoff, Houjun Qian, Yves Renier, Frank Stephan, Carmen Tenholt, Valentin Wohlfarth, and Quantang Zhao', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064801', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064801'), 
                            scrapers.ArticleInfo(name='Control of the Lasing Slice by Transverse Mismatch in an X-Ray Free-Electron Laser', author='Yu-Chiu Chao, Weilun Qin, Yuantao Ding, Alberto A. Lutman, and Timothy Maxwell', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064802', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064802'), 
                            scrapers.ArticleInfo(name='Intrinsic Stabilization of the Drive Beam in Plasma-Wakefield Accelerators', author='A. Martinez de la Ossa, T.\u2009J. Mehrling, and J. Osterhoff', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064803', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064803'), 
                            scrapers.ArticleInfo(name='First Six Dimensional Phase Space Measurement of an Accelerator Beam', author='Brandon Cathey, Sarah Cousineau, Alexander Aleksandrov, and Alexander Zhukov', teaser='A new technique provides the first measurement of all six characteristics of a particle beam, which will help researchers improve beam quality.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.064804', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.064804')]), 
                        scrapers.SectionInfo(name='Condensed Matter: Structure, etc.', articles=[
                            scrapers.ArticleInfo(name='Bond-Breaking Efficiency of High-Energy Ions in Ultrathin Polymer Films', author='R. Thomaz, P. Louette, G. Hoff, S. Müller, J.\u2009J. Pireaux, C. Trautmann, and R.\u2009M. Papaléo', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066101', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066101')]), 
                        scrapers.SectionInfo(name='Condensed Matter: Electronic Properties, etc.', articles=[
                            scrapers.ArticleInfo(name='Ubiquitous Spin-Orbit Coupling in a Screw Dislocation with High Spin Coherency', author='Lin Hu, Huaqing Huang, Zhengfei Wang, W. Jiang, Xiaojuan Ni, Yinong Zhou, V. Zielasek, M.\u2009G. Lagally, Bing Huang, and Feng Liu', teaser='Dislocation defects are often a nuisance in semiconductors, but theoretical work shows they might offer an improved route to producing spin currents.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066401', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066401'), 
                            scrapers.ArticleInfo(name='Correlation-Driven Dimerization and Topological Gap Opening in Isotropically Strained Graphene', author='Sandro Sorella, Kazuhiro Seki, Oleg O. Brovko, Tomonori Shirakawa, Shohei Miyakoshi, Seiji Yunoki, and Erio Tosatti', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066402', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066402'), 
                            scrapers.ArticleInfo(name='Hall Number of Strongly Correlated Metals', author='Assa Auerbach', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066601', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066601'), 
                            scrapers.ArticleInfo(name='Counterpropagating Fractional Hall States in Mirror-Symmetric Dirac Semimetals', author='Yafis Barlas', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066602', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066602'), 
                            scrapers.ArticleInfo(name='Spin Transport and Accumulation in a 2D Weyl Fermion System', author='T. Tzen Ong and Naoto Nagaosa', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.066603', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.066603'), 
                            scrapers.ArticleInfo(name='Model Predictions for Time-Resolved Transport Measurements Made near the Superfluid Critical Points of Cold Atoms and ', author='Yonah Lemonik and Aditi Mitra', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067001', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067001'), 
                            scrapers.ArticleInfo(name='Spin Waves in Detwinned ', author='Xingye Lu, Daniel D. Scherer, David W. Tam, Wenliang Zhang, Rui Zhang, Huiqian Luo, Leland W. Harriger, H.\u2009C. Walker, D.\u2009T. Adroja, Brian M. Andersen, and Pengcheng Dai', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067002', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067002'), 
                            scrapers.ArticleInfo(name='Quantum Spin Ice with Frustrated Transverse Exchange: From a ', author='Owen Benton, L.\u2009D.\u2009C. Jaubert, Rajiv R.\u2009P. Singh, Jaan Oitmaa, and Nic Shannon', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067201', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067201'), 
                            scrapers.ArticleInfo(name='Pauling Entropy, Metastability, and Equilibrium in ', author='S.\u2009R. Giblin, M. Twengström, L. Bovo, M. Ruminy, M. Bartkowiak, P. Manuel, J.\u2009C. Andresen, D. Prabhakaran, G. Balakrishnan, E. Pomjakushina, C. Paulsen, E. Lhotel, L. Keller, M. Frontzek, S.\u2009C. Capelli, O. Zaharko, P.\u2009A. McClarty, S.\u2009T. Bramwell, P. Henelius, and T. Fennell', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067202', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067202'), 
                            scrapers.ArticleInfo(name='Generation of Quantized Polaritons below the Condensation Threshold', author='Peter Cristofolini, Z. Hatzopoulos, Pavlos G. Savvidis, and Jeremy J. Baumberg', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067401', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067401'), 
                            scrapers.ArticleInfo(name='Lattice Energetics and Correlation-Driven Metal-Insulator Transitions: The Case of ', author='Qiang Han and Andrew Millis', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067601', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067601'), 
                            scrapers.ArticleInfo(name='Nematicity and Charge Order in Superoxygenated ', author='Zhiwei Zhang, R. Sutarto, F. He, F.\u2009C. Chou, L. Udby, S.\u2009L. Holm, Z.\u2009H. Zhu, W.\u2009A. Hines, J.\u2009I. Budnick, and B.\u2009O. Wells', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067602', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067602'), 
                            scrapers.ArticleInfo(name='Van der Waals Spin Valves', author='C. Cardoso, D. Soriano, N.\u2009A. García-Martínez, and J. Fernández-Rossier', teaser='A new spin valve design consists of stacked van der Waals layers of graphene and ferromagnetic insulators.', url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067701', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067701'), 
                            scrapers.ArticleInfo(name='Electrical Reservoirs for Bilayer Excitons', author='Ming Xie and A.\u2009H. MacDonald', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.067702', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.067702')]),
                        scrapers.SectionInfo(name='Polymer, Soft Matter, Biological, Climate, and Interdisciplinary Physics', articles=[
                            scrapers.ArticleInfo(name='Controlled Fluidization, Mobility, and Clogging in Obstacle Arrays Using Periodic Perturbations', author='C. Reichhardt and C.\u2009J.\u2009O. Reichhardt', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.068001', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.068001'),
                            scrapers.ArticleInfo(name='Hamiltonian Transformation to Compute Thermo-osmotic Forces', author='Raman Ganti, Yawei Liu, and Daan Frenkel', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.068002', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.068002'),
                            scrapers.ArticleInfo(name='Paradox of Contact Angle Selection on Stretched Soft Solids', author='Jacco H. Snoeijer, Etienne Rolley, and Bruno Andreotti', teaser=None, url='https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.121.068003', pdf_url='https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.121.068003')])
                        ]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
            self.assertEqual(tuple(info), tuple(expected))
