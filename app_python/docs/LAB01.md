## Framework Selection

Flask was chosen for this project because it is lightweight, easy to understand,
and well-suited for small REST services. It allows focusing on DevOps concepts
without unnecessary complexity.

| Framework | Pros | Cons |
|---------|------|------|
| Flask | Simple, lightweight, flexible | No built-in async |
| FastAPI | Async, auto docs | Higher learning curve |
| Django | Full-featured | Overkill for this lab |

## Best Practices Applied

- Environment-based configuration using HOST and PORT variables
- Logging configured using Python logging module
- Error handling for 404 and 500 responses
- PEP8-compliant code structure
- Clear separation of helper functions and routes

These practices improve maintainability, readability, and production readiness.

## API Documentation

### GET /

Returns service, system, runtime, and request information.

```bash
curl http://localhost:5000/
```

### GET /health

Returns application health status and uptime.
This endpoint is intended for monitoring and readiness checks.

```bash
curl http://localhost:5000/health
```

## Testing Evidence

The application was tested locally using curl commands.
Screenshots of the terminal output are included and demonstrate:
- Successful response from the main endpoint (`GET /`)
- Successful response from the health check endpoint (`GET /health`)
- Formatted JSON output of the main endpoint

## Challenges & Solutions

One challenge was collecting system and runtime information in a clean way.
This was solved by using Python standard libraries such as platform, socket,
and datetime.

## GitHub Community

Starring repositories helps support open-source maintainers and improves
project discoverability. Following developers and classmates helps with
collaboration, learning, and professional growth.
