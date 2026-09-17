# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Added

- Call matomo in background if asgi-background is installed by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Add info about background tasks by [@kod-kristoff](https://github.com/kod-kristoff)

## [0.7.1] - 2026-09-17

### Changed

- Use import httpx2 as httpx by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Format Python code in README.md by [@kod-kristoff](https://github.com/kod-kristoff)

### Fixed

- Make default http client follow redirects by [@kod-kristoff](https://github.com/kod-kristoff)

### Internal

- Use httpx2 by [@kod-kristoff](https://github.com/kod-kristoff)

### Removed

- _(deps)_ Remove httpx by [@kod-kristoff](https://github.com/kod-kristoff)
- Remove pre-commit step by [@kod-kristoff](https://github.com/kod-kristoff)

### Build

- _(deps-dev)_ Bump starlette from 0.52.1 to 1.6.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps-dev)_ Bump mkdocs-material from 9.7.3 to 9.7.7 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump idna from 3.11 to 3.15 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/setup-python from 6.3.0 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump pypa/gh-action-pypi-publish from 1.14.0 to 1.14.2 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump re-actors/alls-green from 1.2.2 to 1.3.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 8.2.0 to 10.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/checkout from 7.0.0 to 7.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.5 to 3.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 8.1.0 to 8.2.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/checkout from 6.0.2 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.4 to 2.0.5 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/setup-python from 6.2.0 to 6.3.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump codecov/codecov-action from 6.0.1 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/upload-artifact from 7.0.0 to 7.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 8.0.0 to 8.1.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump rmuir/uv-dependency-submission from 1.0.1 to 1.1.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.2 to 2.0.4 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump codecov/codecov-action from 6.0.0 to 6.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.1 to 2.0.2 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump pypa/gh-action-pypi-publish from 1.13.0 to 1.14.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump rmuir/uv-dependency-submission from 1.0.0 to 1.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump codecov/codecov-action from 5.5.2 to 6.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 7.6.0 to 8.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/download-artifact from 8.0.0 to 8.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 1.1.1 to 2.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 7.3.1 to 7.6.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/upload-artifact from 6.0.0 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 7.3.0 to 7.3.1 by [@dependabot[bot]](https://github.com/dependabot[bot])

## [unreleased]

### Added

- Call matomo in background if asgi-background is installed by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Add info about background tasks by [@kod-kristoff](https://github.com/kod-kristoff)

### Internal

- Also verify background call gets made by [@kod-kristoff](https://github.com/kod-kristoff)

### Removed

- Remove ruff.preview = true, update codes by [@kod-kristoff](https://github.com/kod-kristoff)

## [0.7.1] - 2026-09-17

### Changed

- Use import httpx2 as httpx by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Format Python code in README.md by [@kod-kristoff](https://github.com/kod-kristoff)

### Fixed

- Make default http client follow redirects by [@kod-kristoff](https://github.com/kod-kristoff)

### Internal

- Use httpx2 by [@kod-kristoff](https://github.com/kod-kristoff)

### Removed

- _(deps)_ Remove httpx by [@kod-kristoff](https://github.com/kod-kristoff)
- Remove pre-commit step by [@kod-kristoff](https://github.com/kod-kristoff)

### Build

- _(deps-dev)_ Bump starlette from 0.52.1 to 1.6.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps-dev)_ Bump mkdocs-material from 9.7.3 to 9.7.7 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump idna from 3.11 to 3.15 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/setup-python from 6.3.0 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump pypa/gh-action-pypi-publish from 1.14.0 to 1.14.2 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump re-actors/alls-green from 1.2.2 to 1.3.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 8.2.0 to 10.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/checkout from 7.0.0 to 7.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.5 to 3.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 8.1.0 to 8.2.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/checkout from 6.0.2 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.4 to 2.0.5 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/setup-python from 6.2.0 to 6.3.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump codecov/codecov-action from 6.0.1 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/upload-artifact from 7.0.0 to 7.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 8.0.0 to 8.1.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump rmuir/uv-dependency-submission from 1.0.1 to 1.1.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.2 to 2.0.4 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump codecov/codecov-action from 6.0.0 to 6.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 2.0.1 to 2.0.2 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump pypa/gh-action-pypi-publish from 1.13.0 to 1.14.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump rmuir/uv-dependency-submission from 1.0.0 to 1.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump codecov/codecov-action from 5.5.2 to 6.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 7.6.0 to 8.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/download-artifact from 8.0.0 to 8.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump j178/prek-action from 1.1.1 to 2.0.1 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 7.3.1 to 7.6.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump actions/upload-artifact from 6.0.0 to 7.0.0 by [@dependabot[bot]](https://github.com/dependabot[bot])
- _(deps)_ Bump astral-sh/setup-uv from 7.3.0 to 7.3.1 by [@dependabot[bot]](https://github.com/dependabot[bot])

## [0.7.1] - 2026-09-17

### Changed

- Use import httpx2 as httpx by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Format Python code in README.md by [@kod-kristoff](https://github.com/kod-kristoff)

### Fixed

- Make default http client follow redirects by [@kod-kristoff](https://github.com/kod-kristoff)

### Internal

- _(deps)_ Add httpx2 by [@kod-kristoff](https://github.com/kod-kristoff)

### Removed

- _(deps)_ Remove httpx by [@kod-kristoff](https://github.com/kod-kristoff)

## [0.7.0] - 2026-09-11

### Fixed

- Report correct cip by [@kod-kristoff](https://github.com/kod-kristoff)

## [0.6.2] - 2026-03-03

### Changed

- Fix typing issues by [@kod-kristoff](https://github.com/kod-kristoff)
- Update code to 3.10 by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Change badge to rolling by [@kod-kristoff](https://github.com/kod-kristoff)

### Fixed

- Check if scope contains state inside PerfMsTracker by [@kod-kristoff](https://github.com/kod-kristoff)

## [0.6.1] - 2025-12-10

### Added

- Allow to allow and ignore calls based on http method by [@kod-kristoff](https://github.com/kod-kristoff)
- Add kwarg for setting http_timeout by [@kod-kristoff](https://github.com/kod-kristoff)

### Changed

- Use matomo-core instead by [@kod-kristoff](https://github.com/kod-kristoff)
- Use PerfMsTracker from matomo-core by [@kod-kristoff](https://github.com/kod-kristoff)

### Documentation

- Update README.md by [@kod-kristoff](https://github.com/kod-kristoff)

### Fixed

- Record error and error message by [@kod-kristoff](https://github.com/kod-kristoff)

## [0.6.0] - 2024-03-13

### Changed

- Use post call for tracking

## [0.5.0] - 2023-11-06

### Changed

- Don't be so strict about dependency versions.

### Internal

- Use rye instead of poetry.

## [0.4.1] - 2023-05-29

### Added

- Track urlref. PR [#21](https://github.com/spraakbanken/asgi-matomo/pull/21) by [@kod-kristoff](https://github.com/kod-kristoff).

### Fixed

- Respect x-forwarded-for. PR [#18](https://github.com/spraakbanken/asgi-matomo/pull/18) by [@kod-kristoff](https://github.com/kod-kristoff).

## [0.4.0] - 2023-05-25

### Documentation

- Add documentation [here](https://spraakbanken.github.io/asgi-matomo)

### Fixed

- Handle lifespan correctly. PR [#13](https://github.com/spraakbanken/asgi-matomo/pull/13) by [@kod-kristoff](https://github.com/kod-kristoff).

## [0.3.2] - 2023-05-23

### Added

- Add PerfMsTracker. PR [#10](https://github.com/spraakbanken/asgi-matomo/pull/10) by [@kod-kristoff](https://github.com/kod-kristoff).

### Internal

- Bump starlette to 0.27

## [0.3.0] - 2023-05-22

### Added

- Allow setting route-details

### Documentation

- Add release notes header

### Fixed

- Ignore mypy lints

### Internal

- Update chore targets

## [0.2.0] - 2023-05-12

### Added

- Exclude paths from tracking
- Pass custom variables to middleware
- Track status_code and method

### Documentation

- Update readme

### Fixed

- Use send_image=0

### Internal

- Add git-cliff config
- Add more metadata
- Add test that real client is created

## [0.1.4] - 2023-05-10

### Fixed

- Measure time in ms

## [0.1.3] - 2023-05-10

### Fixed

- Add debug prints
- Onyl track first server address

### Internal

- Bump version
- Add bump2version
- Update Makefile

## [0.1.1] - 2023-05-09

### Added

- Import middleware from karp-backend

### Documentation

- Write README.md
- Add codecov badge

### Fixed

- Add log call for tracking response

### Internal

- Poetry setup
- Fix type hint
- Bump version

<!-- generated by git-cliff -->
