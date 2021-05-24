# gcp

[![Code style: black][black-badge]][black]

this is my own copy of the database of pulsars in globular clusters maintained by Paulo Freire [**here**][gcp]. if you end up using the data in this repository for your work, please mention the url of Paulo Freire's cite as a footnote in your paper. i chose to scrap the [**HTML version**][gcp] of the database and parse it into JSON. the code that does all that is in [**scrap.py**](scrap.py), and the data resides (in all of its JSONic glory) in [**gcp.json**](gcp.json). the data is updated every Friday, at midnight (in UTC time). this repository will eventually power the [**koshka**][koshka] package, which aims to make accessing all pulsar and radio transient related catalogues easier.

[black]: https://github.com/psf/black
[gcp]: http://www.naic.edu/~pfreire/GCpsr.html
[koshka]: https://github.com/astrogewgaw/koshka
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
