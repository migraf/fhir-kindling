# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.0.0] - 2023-
Improve packaging with poetry to slim down library size with optional extras for datascience features.
Add support for Python 3.9+.
Code base cleanup and refactoring.

### Changed
- **Breaking:** Renamed `FHIRQuery` classes to `FhirQuerySync` and `FhirQueryAsync` for naming consistency.
- **Breaking:** Renamed `FHIRQueryParameters` class to `FhirQueryParameters` for naming consistency.
- **Breaking:** Query response `.save()` method now only supports saving as XML or JSON file. To serialize resources and bundles use
    the `flatten` function from the `serde` package. Requires installation of the `ds` extra.
- **Breaking:** Moved `ServerSummary` and summary functionality into separate module.
- Improve packaging with poetry and optional extras for datascience features and web app.
- Optional dependencies for [`ds`, `app`] can be installed using `pip install fhir_kindling[{extra}]`.
- Split batch transactions into separate module to slim down `FhirServer` class.

### Added
- Optional progress bar for `summary`, `get_many`, `add_all` and `transfer` methods.
- Additional property `resource_list` on `FhirQueryResponse` to get a list of all resources from the response.

### Removed
- Removed `to_dfs()` method on query response object. Use `flatten` function from the `serde` package instead.
    Requires installation of the `ds` extra.
- Removed `requests-oauthlib` in favor of `authlib`.
## [0.9.0] - 2022-07-21
Asynchronous API for CRUD operations against fhir servers.

### Changed
- Switched http client library from requests [httpx](https://www.python-httpx.org/)
- removed requests-oauthlib in favor of authlib for oauth2 authentication flow
- `FHIRQuery` class renamed to `FhirQuerySync` to allow for sync and async version
- moved resolving response pagination from `QueryReponse` to the sync and async query classes
- getting multiple resources via `server.get_many()` now uses proper batch requests

### Added
- `FhirQueryAsync` class for async queries against a server
- asynchronous counterparts for CRUD operations in the `FHIRServer` class using the same API:
  - `query_async()`
  - `raw_query_async()`
  - `get_async()`
  - `get_many_async()`
  - `add_async()`
  - `add_all_async()`
  - `add_bundle_async()`
  - `update_async()`
  - `delete_async()`


## [0.8.0] - 2022-03-18
Resource transfer between servers and querying resources by reference.  
`get`, `get_many` for querying resource by reference
`server.transfer(other_server, query_result)` for transferring resources

### Changed
- `FhirServer` constructor now accepts two additional optional parameters, `auth` and `headers` that will be used for the
  instance's `requests` session.

### Added
 - [x] `server.get(reference)` get a single resource from the server, based on relative path/reference.
 - [x] `server.get_many(references)` get multiple resources from the server, based on relative path/reference.
 - [x] `server.transfer(other_server, query)` transfer resources matching the query from one server to another. Also requests
   resources referenced by the resources matching to maintain referential integrity on the new server.
 - [x] `query.all(page_callback=callback, count=50)` callback functions and count for pagination resolving in query responses.

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
