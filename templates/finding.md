### {ID} — {Title}

**Severity**: {Severity}  
**Confidence**: {Confidence}  
**Status**: {Status}  
**Effort**: {Effort}  
**Regression risk**: {Regression risk}

**Preconditions**:
{What must be true for this finding to trigger?}

**Exploitability / Blast radius**:
{How easily can this be triggered? What is the impact domain?}

**Likelihood / Exposure evidence**:
{What is the probability of this happening? What evidence shows the path is reachable?}

**Evidence**:
- `{file_path}:{start_line}-{end_line}`
```code_language
{snippet}
```

**Taint chain** (Security only):
- Source: {Input source}
- Transforms: {Mutations}
- Validation Boundary: {Where is it checked, or lacking check?}
- Sink: {Execution or rendering sink}
- Impact: {Resulting capability}

**Observed**:
{Description of the observed behavior}

**Expected**:
{Description of the expected behavior}

**Root cause**:
{Explanation of the root cause}

**Impact**:
{Explanation of the impact}

**Reproduction**:
{Steps or commands to reproduce the issue}

**Remediation**:
{Minimal safe fix required to resolve the issue}

**Validation**:
{Commands or tests to run to verify the fix}
