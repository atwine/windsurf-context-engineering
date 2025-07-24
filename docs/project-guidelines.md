# Project Guidelines for Cascade

These are the global rules and best practices to follow for all projects within this directory.

## General
- **Clarity:** Write clear, readable, and maintainable code.
- **Modularity:** Break down complex problems into smaller, manageable functions or classes.
- **Documentation:** Add docstrings to all public modules, classes, and functions.
- **Testing:** Write comprehensive tests for all functionality.
- **Version Control:** Use meaningful commit messages and maintain clean git history.

## Python
- **Style:** Follow PEP 8 style guidelines.
- **Dependencies:** List all project dependencies with their versions in `requirements.txt`.
- **Testing:** Use the `pytest` framework for testing.
- **Security:** Never hardcode secrets or credentials. Use environment variables (`.env` file) for configuration.
- **Type Hints:** Use type hints for function parameters and return values.
- **Virtual Environments:** Always use virtual environments for project isolation.

## JavaScript/TypeScript
- **Style:** Follow ESLint and Prettier configurations.
- **Dependencies:** Use `package.json` and `package-lock.json` for dependency management.
- **Testing:** Use Jest or similar testing frameworks.
- **Security:** Validate all user inputs and sanitize outputs.
- **Modern Syntax:** Use ES6+ features and async/await for asynchronous operations.

## Error Handling
- Implement robust error handling, especially for network requests and file I/O.
- Use try-except blocks to catch specific exceptions.
- Log errors with meaningful messages.
- Provide user-friendly error messages.
- Implement graceful degradation where possible.

## Code Organization
- **File Structure:** Organize code into logical modules and directories.
- **Naming:** Use descriptive names for variables, functions, and classes.
- **Comments:** Add comments for complex logic, not obvious code.
- **Constants:** Define constants at the module level, not inline.
- **Imports:** Group imports logically (standard library, third-party, local).

## Documentation
- **README:** Every project must have a comprehensive README.md.
- **API Documentation:** Document all public APIs and endpoints.
- **Setup Instructions:** Provide clear installation and setup instructions.
- **Usage Examples:** Include practical usage examples.
- **Changelog:** Maintain a changelog for significant updates.

## Security Best Practices
- **Input Validation:** Validate and sanitize all user inputs.
- **Authentication:** Implement proper authentication and authorization.
- **HTTPS:** Use HTTPS for all network communications.
- **Dependencies:** Regularly update dependencies and scan for vulnerabilities.
- **Secrets Management:** Use environment variables or secret management systems.

## Performance
- **Optimization:** Write efficient algorithms and data structures.
- **Caching:** Implement appropriate caching strategies.
- **Database:** Use proper indexing and query optimization.
- **Monitoring:** Include logging and monitoring capabilities.
- **Resource Management:** Properly manage memory and file handles.
