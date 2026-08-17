# API Documentation Gate

> **Source lineage:** HQE-Workbench `mcp-server/prompts/server/resources/gates/api-documentation/`. Paraphrased for HQE Skill use.

## Purpose / When to Activate

The API Documentation gate ensures that API documentation is complete, consistent, and useful for consumers. Activate it when producing or reviewing API reference docs, OpenAPI specs, endpoint guides, or developer onboarding material.

## Pass Criteria

- Each endpoint description includes the HTTP method and path.
- All request parameters are documented with types and examples.
- Complete request and response examples are provided.
- Error codes and messages are documented.
- Authentication requirements are specified.
- Rate limiting information is included when applicable.

## Forbidden Patterns / Failure Modes

| Pattern | Risk |
| :--- | :--- |
| Missing parameter types | Consumers cannot construct valid requests. |
| No response examples | Error handling is undefined. |
| Undocumented error codes | Clients fail silently. |
| Missing auth requirements | Unauthorized access attempts. |
| Out-of-date examples | Documentation drift from implementation. |

## Activation Rules

- **Artifact types:** API reference docs, OpenAPI/YAML specs, README endpoints section, developer guides.
- **Workflow triggers:** documentation generation, API design review, PR review for API changes.
- **Explicit request:** not required.

## Retry / Escalation Guidance

1. **First failure:** Add the missing sections and examples.
2. If the implementation has changed, update the code first and regenerate docs from the source of truth.
3. For public APIs, cross-check examples with an actual request/response before claiming completion.
