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

## Loading Articles 
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
 