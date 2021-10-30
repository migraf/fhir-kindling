# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


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
