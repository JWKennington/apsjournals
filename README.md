# APS Journals
_A pythonic interface for browsing APS_

The `apsjournals` library is a collection of tools used for exploring American 
Physical Society publications via python. 

Test Result: [![CircleCI](https://circleci.com/gh/JWKennington/apsjournals/tree/master.svg?style=svg)](https://circleci.com/gh/JWKennington/apsjournals/tree/master)

## Motivation
Admittedly, the APS website is well-built. Why `apsjournals` then? 
1. The APS website does not offer an official API. This library offers a set of usable abstractions 
to help explore some of the available data.
1. It is not possible to download an entire Issue as a single PDF in the current website. 
Future versions of `apsjournals` will offer such behavior.
1. Why not? Interacting with APS publications via Python is fun.

## Loading Articles for a Journal Issue
The `apsjournals` library offers several ways to load articles. The easiest of which
is by picking a Journal, then specifying a volume and issue number. The library will then
load the entire issue, including all articles. For example:
```python
>>> from apsjournals import PRL
>>> PRL
Journal('Physical Review Letters')

>>> PRL.issue(121, 6)
Issue('Physical Review Letters', 121, 6)

>>> PRL.issue(121, 6).articles[:3]
[Article('Magnetic Levitation Stabilized by Streaming Fluid Flows'),
 Article('First Six Dimensional Phase Space Measurement of an Accelerator Beam'),
 Article('Ubiquitous Spin-Orbit Coupling in a Screw Dislocation with High Spin Coherency')]
```
 
## Download Journal Articles
In addition to surveying which articles are in an issue, `apsjournals` is also capable of downloading 
articles, either individually or as an entire issue. In the latter case, a cover page and table of contents
will also be added to the pdf (including appropriately linked bookmarks).

### Authentication
The first step to downloading articles is authentication. You _must_ be a valid APS member. this library
abides by all APS Terms and Conditions, and consequently relies on you for credentials to access
APS material. Authentication can be performed by using the `authenticate` function:

```python
>>> import apsjournals
>>> apsjournals.authenticate('username', 'password')
```

This will set a session cookie required for pdf downloads. 

### Downloading an Article
After authenticating, it is then possible to download articles from an issue individually or as a whole.
To download an individual article, use the `pdf` method of the `Article` instance.
Specifically:

```python
>>> journal = apsjournals.PRL
>>> issue = journal.issue(121, 6)
>>> article = issue.articles[3]
>>> article.pdf('path/to/file.pdf')
```

This will download the article as a pdf to the given location. 

### Download an Entire Issue
In order to download all the articles at once, simply use the `pdf` method of the `Issue` instance! For
example:

```python
>>> issue.pdf('path/to/file.pdf')
```


 