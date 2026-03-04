# Changelog

All notable changes to the Miniflux skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3](https://github.com/dorogoy/miniflux-skill/compare/v0.2.2...v0.2.3) (2026-02-16)


### Bug Fixes

* add required environment variables to registry metadata ([23ed5fe](https://github.com/dorogoy/miniflux-skill/commit/23ed5fed61c39007d4cff8e41f9df83daada722d))

## [0.2.2](https://github.com/dorogoy/miniflux-skill/compare/v0.2.1...v0.2.2) (2026-02-16)


### Bug Fixes

* remove hardcoded MINIFLUX_URL and auto-install ([6f04c53](https://github.com/dorogoy/miniflux-skill/commit/6f04c53befee7ebcf6ee32333627b92d430ceac1))

## [0.2.1](https://github.com/dorogoy/miniflux-skill/compare/v0.2.0...v0.2.1) (2026-02-15)


### Bug Fixes

* add release-please-manifest.json to .clawhubignore ([5589053](https://github.com/dorogoy/miniflux-skill/commit/5589053477144eea436d5c2d2bd10098dabc04d8))

## [0.2.0](https://github.com/dorogoy/miniflux-skill/compare/v0.1.0...v0.2.0) (2026-02-15)


### Features

* add toggle-bookmark command ([bc529e4](https://github.com/dorogoy/miniflux-skill/commit/bc529e4d49aa02a26d5f5cc1c7158805db86efb5))


### Bug Fixes

* add .clawhubignore to exclude release-please-config.json and tests/ from clawhub package ([d694a16](https://github.com/dorogoy/miniflux-skill/commit/d694a16be5fab6141077e52170fd87f571f664ee))
* ensure release-please-action has proper permissions ([d45ad5f](https://github.com/dorogoy/miniflux-skill/commit/d45ad5f3dfdce1f0a31ff0e7d5b6409c447e426a))

## [Unreleased]

## [0.1.0] - 2026-02-14

### Added
- Initial skill implementation
- REST API v1 integration with X-Auth-Token authentication
- Full feed management (list, create, update, delete, refresh)
- Categories management
- Entries with advanced filters (status, search, limit, etc.)
- Counter support for unread/read tracking
- Discovery from URLs
- Python client integration with official `miniflux` package
- Comprehensive documentation (SKILL.md and README.md)
- GitHub Actions workflows for testing and releases
- Initial `.gitignore` for Python projects
