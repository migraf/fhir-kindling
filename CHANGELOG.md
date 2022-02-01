# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [0.7.0] - 2022-01-31
Update a list of resources on the server. CSV/Pandas serialization of resources and query responses.

### Added
 - [x] `server.update(resources)` which updates a list of resources stored on the server
 - [x] Recursive resource flattening for csv/tabular serialization
 - [x] `query_response.save(path, format="csv)` to save the results of a query to csv

### Changed
- `server.query(params)` the query method now directly accepts query parameters


## [0.6.0] - 2022-01-19
Query Response with included resources. Reworked Generators

### Added
 - [x] Query response now stores and parses included resources
 - [x] Generator parameters for Resources and Fields
 - [x] Field generators for generating resource fields based on probabilistic choices or a generator function
 - [x] Resource generator field values based on static value or list
 - [x] Patient based data set generator 

### Changed
- Query interface `where, include, has` now can add query parameters based on method arguments or parameter objects.




## [0.5.0] - 2021-11-12

Query Parameters, include/revinclude, reverse chaining.  

### Added
 - [x] Query Parameters classes, for regular queries, including resources and reverse chaining
 - [x] Support for `_include` and `_revinclude` via `query.include()`
 - [x] Reverse chaining support via `query.has()`
 - [x] Parsing parameters from given URL/ coverting parameters to query url

### Changed
- Query interface `where, include, has` now can add query parameters based on method arguments or parameter objects.




## [0.4.0] - 2021-11-12

Server summary, deleting resources, removed initial CLI.

### Added

- [x] Getting a list of all resources on the server based on capabilities
- [x] Plots for server and resource summary
- [x] `server.delete()` method to delete resources based on ids

## [0.3.0] - 2021-10-30

Response classes, reference parsing and basic xml support

### Added

XML output format and resolving xml pagination. Response objects containig resources and references

### Changed

Outsourced resolving of response pagination into response classes

### Fixed

## [0.2.0] - 2021-09-18

FHIR server and query API

### Added

Classes for fhir servers and queries. Oauth2/OIDC support.

### Changed

Moved location of cli

### Fixed

## [0.1.0] - 2021-08-24

Initial cli

### Added

### Changed

### Fixed

Hashing order guarantees the right index of the query.json file in the hash
