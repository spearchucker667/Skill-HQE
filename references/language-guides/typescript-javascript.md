# TypeScript & JavaScript Diagnostic Guide

## 1. Project Orientation & Manifests
- **Package Manifests**: `package.json`, `pnpm-workspace.yaml`, `lerna.json`, `turbo.json`.
- **Lockfiles**: `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`.
- **TypeScript Configuration**: `tsconfig.json`, `tsconfig.build.json`.

## 2. Common Defect Patterns
1. **Unchecked Null/Undefined**: Optional chaining (`?.`) misused or missing fallbacks leading to `TypeError: Cannot read properties of undefined`.
2. **Unhandled Promise Rejections**: Missing `.catch()` or floating unawaited async calls causing unhandled rejections or silent failures.
3. **Prototype Pollution**: Unsafe object merging (`Object.assign({}, obj)` or recursive merges) allowing prototype injection.
4. **Memory Leaks**: Event listeners, global subscriptions, or closures holding onto large DOM/buffer references.
5. **Type Assertions & `any`**: Overuse of `as unknown as T` or `any` masking breaking runtime schema changes.
6. **ESM / CommonJS Interop**: Mismatched default vs named imports causing runtime crashes in bundle outputs.

## 3. Verification & Validation Commands
```bash
# Typecheck
npx tsc --noEmit

# Lint
npx eslint . --max-warnings=0

# Tests
npm test
npx vitest run
npx jest --runInBand
```
