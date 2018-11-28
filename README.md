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

    pip3 install searchguard

Set the environment variables

    export SEARCHGUARD_API_URL="https://www.example.com:1234/_searchguard/api"
    export SEARCHGUARD_API_USER="foo"
    export SEARCHGUARD_API_PASS="bar"

## Future work ##

* Add code for managing rolesmapping
* Add code for managing actiongroups

## Legal

* Elasticsearch is a trademark of Elasticsearch BV, registered in the U.S. and in other countries.
* Search Guard is a trademark of floragunn GmbH, registered in the U.S. and in other countries.
* Byte Internet is not affiliated with either Elasticsearch BV / floragunn GmbH.
