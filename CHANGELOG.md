# Changelog

## [0.2.0] - 01.09.2024

### Added
- **Basic User Authentication:** Implemented authentication based on JWT tokens
- **User Models and Schemas:** Added models and schemas related to user management
- **Task Models and Schemas:** Added models and schemas for task management
- **API Endpoints:** Created basic API endpoints for CRUD operations
- **Logging System:** Implemented a logging system for better traceability
- **Unit Tests:** Added unit tests to ensure code reliability
- **MongoDB Integration:** Included MongoDB operations for data management
- **Docker Configuration:** Added Docker configuration files for containerization
- **Short README.md Description:** Updated the README.md with a brief project overview

## [0.3.0] - 09.09.2024

### Fixed
- **Release Pipeline:** Minor bug fixes + typos + formatter fixes (trailing spaces and so on)
- **Database:** Added additional conditions for checking if user already exists in the database, when
trying to add a new user
### Added
- **Pre-commit Hooks:** Added basic pre-commit hooks for checking and fixing style-related errors
- **CI Pipeline:** Added caching mechanism for pre-commit hooks
- **Database:** Refactoring of the code to one solid 'Database' class
- **New attributes for tasks:** Added 2 new fields 'label' and 'deadline' and corresponding logic
- **Project Description:** Added descriptions of 'test' and 'release' pipelines in README.md
