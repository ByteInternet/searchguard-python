# searchguard-python
Unofficial Python library for Search Guard (a security solution for Elasticsearch)

## Installation ##

**This library requires a Search Guard subscription (or trail license). Information can be found on https://search-guard.com/.**

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
