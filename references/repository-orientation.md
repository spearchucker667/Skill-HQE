# Repository Orientation

Phase 0 of any HQE audit is Orientation. This is mandatory before making any broad claims or deep analyses.

## Key Identification Objectives
Identify and document the following:
1. **Languages & Frameworks**: What is the primary stack?
2. **Build Systems & Package Managers**: Is it Cargo, npm, Maven, Gradle, Go modules?
3. **Architecture Boundaries**: Where are the application vs. library boundaries? What are the entrypoints?
4. **Manifests**: Locate `package.json`, `Cargo.toml`, `go.mod`, etc.
5. **Testing Frameworks**: What is used for testing, and how are tests invoked?
6. **CI/CD Workflows**: Look in `.github/workflows/`, `.gitlab-ci.yml`, etc.
7. **Security Boundaries**: Where does external input enter the system? Where are the trust boundaries?
8. **Documentation**: What are the sources of truth? (e.g., `README.md`, `docs/`)

## Creating a Baseline Map
Create a concise architecture map or mental model of the repository. You should know:
- How to build the project.
- How to run the tests.
- Where the critical logic lives.

Do not guess build commands. Discover them from repository evidence (e.g., looking at CI workflows or package scripts). If you run commands, capture the exact command, exit status, and meaningful stdout/stderr.
