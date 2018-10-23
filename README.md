# searchguard-python

[![build status](https://travis-ci.org/ByteInternet/searchguard-python.svg?branch=master)](https://travis-ci.org/ByteInternet/searchguard-python)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Unofficial Python library for Search Guard (a security solution for Elasticsearch)

## Installation ##

**This library requires a Search Guard subscription (or trial license). Information can be found on https://search-guard.com/.**

Make sure enterprise modules are enabled in your elasticsearch.yml:

    searchguard.enterprise_modules_enabled: true

Make sure backend role management in your elasticsearch.yml is set to either of the two options below:

    searchguard.roles_mapping_resolution: *[BACKENDROLES_ONLY|BOTH]*

Install the library:

    pip install searchguard

## Work in progress ##

* Add code for managing rolesmapping
* Add code for managing actiongroups
* Allow password customization (e.g. length)
* Add optional password argument to create_user
