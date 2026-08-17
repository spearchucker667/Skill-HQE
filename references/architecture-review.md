# Architecture Review Guide

When performing an architecture audit (`/HQE architecture`), focus on boundary enforcement, component cohesion, and data flows.

## 1. Core Architectural Quality Dimensions
1. **Module Boundaries & Coupling**: Are internal modules leaking abstractions or importing directly from private internal packages of other modules?
2. **Layering Violations**: Are UI/presentation layers calling database queries directly, bypassing domain services?
3. **State Management**: Is mutable global state shared without synchronization or explicit lifecycle management?
4. **API & Protocol Contracts**: Are schemas backward compatible? Are versioning strategies respected?
5. **Extensibility vs Overengineering**: Is the codebase suffering from premature abstraction or rigid boilerplate?
