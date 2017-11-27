# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Fixed
* `incidents/{id}/snooze` was not deprecated and requires old logic from `_do_action`. Fixed.
* `trigger_summary_data` attribute was removed from incident response, removed `has_subject` function which referenced this.
### Added
* `incidents/reassign` is a new endpoint, added logic for this.
* Tests for the new incidents behavior.
* LogEntries default to adding include[]=channels for list and show to get "custom details".

## [0.36.3] - 2017-08-10

### Fixed
- Bug with Incident.ack/resolve. This should now work.

### Changed
- Renamed requester_id to requester to make it more clear you pass an e-mail now instead of user id on various Incident methods.

## [0.36.2] - 2017-08-07

### Fixed
- `incidents/{id}/{verb}` has been deprecated with v2 of the PagerDuty API. Fixed.

### Added
- Tests for the new incidents behavior.

## [0.36.1] - 2017-07-11

### Added
- This CHANGELOG file.
- `FinalSchedule`, `RenderSchedule` containers added to provide more readable responses.

## Removed
- `Entries` collection and `entries` attribute from `Schedule` from v2 module as they're not supported in the v2 API.

## Changed
- `Events` class now has a default `Requester` to improve ergonomics.


## [0.36.0] - 2017-07-05

### Added
- Forked __init__.py into new v2, common, events modules. These are meant to support the v2 REST API without breaking existing users of pygerduty.
- Lots of tests for v2 module.
- Usage of v2 library to README
- Overview of modules to README

### Changed
- Moved inline json into fixture files to clean up unit tests.

### Fixed
- setup.py test integrations to properly fail on Travis CI.

## [0.35.2] - 2016-12-07
## [0.35.1] - 2016-08-30
## [0.35.0] - 2016-06-04
## [0.34.0] - 2016-03-10
## [0.33.0] - 2016-03-07
## [0.32.1] - 2016-02-03
## [0.32.0] - 2016-02-02
## [0.31.0] - 2016-01-18
## [0.30.1] - 2016-01-04
## [0.30.0] - 2015-12-07
## [0.29.1] - 2015-11-07
## [0.29.0] - 2015-10-09
## [0.28.1] - 2015-09-30
## [0.28] - 2015-04-01
## [0.27] - 2015-03-04
## [0.26] - 2015-03-04
## [0.25] - 2015-01-02
## [0.24] - 2014-12-09
## [0.23] - 2014-12-08
## [0.22] - 2014-07-01
## [0.21] - 2014-06-22
## [0.20] - 2014-05-30
## [0.19] - 2014-02-19
## [0.18] - 2013-11-30
## [0.17] - 2013-10-23
## [0.16] - 2013-10-01
## [0.15] - 2013-09-25
## [0.14] - 2013-08-22
## [0.13] - 2013-08-07
## [0.12] - 2012-12-16
## [0.12] - 2012-12-16
## [0.11] - 2012-12-13
## [0.1] - 2012-12-12
