# Skill Quality Assessment Guidelines

Detailed criteria for providing effective, actionable feedback on skills.

## Severity Criteria

### Critical

**Characteristics**:
- Broken code that won't compile/run
- Wrong method/class names that cause immediate failures
- Non-existent references to APIs that don't exist
- Information that blocks task completion

**Examples**:
- "Skill uses `greaterThan()` but method is actually `moreThan()`"
- "References `inspectDayContainingShift()` which doesn't exist in Timeline"
- "Example code missing required import statement"
- "SQL syntax error in query example"

**Test**: Would following this skill example verbatim cause code to break?

### High

**Characteristics**:
- Missing essential domain knowledge
- Critical context gaps that cause confusion
- Known bugs/gotchas not documented
- Significantly outdated information

**Examples**:
- "Doesn't explain ComplianceShift has 3 different duration properties"
- "Missing warning about builder timestamp overlap bug"
- "No mention of age filtering required at two levels"
- "API authentication completely undocumented"

**Test**: Would having this information prevent significant confusion or mistakes?

### Medium

**Characteristics**:
- Inefficient approaches documented
- Minor confusion or ambiguity
- Hard to find information
- Poor organization

**Examples**:
- "Unclear when to use single-shift vs multi-shift pattern"
- "ShiftFilters buried in middle of large file"
- "Five similar examples when two would suffice"
- "File organization makes related info hard to locate"

**Test**: Does this slow down task completion or cause minor friction?

### Low

**Characteristics**:
- Nice-to-have improvements
- Polish and optimization
- Minor verbosity
- Stylistic preferences

**Examples**:
- "Could add quick reference table for Timeline methods"
- "Example could be 2 lines shorter"
- "Section heading could be more descriptive"
- "Might benefit from visual diagram"

**Test**: Would this be a minor quality-of-life improvement?

## Area Definitions

### accuracy
Information that is factually wrong: wrong method names, incorrect syntax, false statements, outdated APIs.

### missing_context
Essential domain knowledge, concepts, or context not documented that would have prevented confusion or errors.

### non_existent
References to methods, classes, APIs, or features that don't actually exist in the codebase or system.

### broken_example
Code examples that don't work when used: syntax errors, missing imports, wrong logic, compilation failures.

### navigation
Difficulty finding information: poor file organization, missing cross-references, unclear structure, lack of index.

### verbosity
Content that is too wordy: redundant examples, obvious explanations for target audience, duplicate information.

### examples
Issues with examples: too many, too few, not representative, too simple, too complex, unclear purpose.

### guidance
Missing workflow or procedural information: unclear decision criteria, missing process steps, ambiguous instructions.

### structure
File and content organization problems: files should be split/merged, sections in wrong order, unclear hierarchy.

## Action Guidelines

### Problems (fix/replace/remove/add/clarify)

**fix**: Correct existing wrong information while keeping structure
- Use for: Wrong method names, syntax errors, factual mistakes
- Example: "Fix greaterThan() to moreThan()"

**replace**: Substitute entire section with different content
- Use for: Outdated approaches, fundamentally wrong explanations
- Example: "Replace authentication section with OAuth2 flow"

**remove**: Delete content entirely
- Use for: Redundant examples, obsolete information, obvious statements
- Example: "Remove examples 3-5, pattern clear after first two"

**add**: Insert new content
- Use for: Missing context, undocumented features, gaps in knowledge
- Example: "Add section explaining three duration properties"

**clarify**: Make existing content clearer without major changes
- Use for: Ambiguous instructions, unclear examples
- Example: "Clarify when to use each Timeline inspection method"

### Improvements (condense/expand/restructure/reword/move/merge/split)

**condense**: Reduce verbosity while preserving meaning
- Use for: Wordy sections, redundant examples
- Example: "Condense five examples to two canonical ones"

**expand**: Add more detail or context
- Use for: Insufficient explanation, missing examples
- Example: "Expand age filtering section with multi-shift example"

**restructure**: Reorganize within same file
- Use for: Logical flow issues, poor section ordering
- Example: "Restructure to put common patterns before edge cases"

**reword**: Rephrase for clarity
- Use for: Confusing wording, jargon, ambiguous phrasing
- Example: "Reword to use simpler language for target audience"

**move**: Relocate content to different file/section
- Use for: Content in wrong place, navigation issues
- Example: "Move ShiftFilters to SINGLE_SHIFT_PATTERNS.md"

**merge**: Combine multiple sections/files
- Use for: Fragmented related content, too many small files
- Example: "Merge FORMS.md and VALIDATION.md into PROCESSING.md"

**split**: Separate into multiple sections/files
- Use for: Files too large, mixing unrelated content
- Example: "Split PATTERNS.md into SINGLE_SHIFT and MULTI_SHIFT"

## Writing Quality Suggestions

### Be Specific

❌ "Examples need improvement"
✅ "Five examples in MULTI_SHIFT_PATTERNS.md (lines 60-120) show weekly calculations with only minor variations - keep first two, reference real constraints for others"

❌ "Missing information"
✅ "Missing explanation that ComplianceShift has three duration properties: duration (includes breaks), labour (excludes breaks), and break (break time only)"

### Explain Impact

Every suggestion should include rationale explaining:
- What problem this caused
- Why it matters
- How it affected task completion

**Good rationale examples**:
- "Code breaks immediately when method called"
- "Spent 15 minutes debugging before checking source"
- "Required human intervention to explain concept"
- "Caused test failure with confusing error message"

### Provide Context

Help the skill architect understand:
- What you were trying to do
- Where you looked for the answer
- What you tried that didn't work
- How you eventually solved it

### Offer Multiple Suggestions

When possible, provide alternatives:

```json
"suggestions": [
  "Update all greaterThan() to moreThan()",
  "Add grep command to verify: grep 'greaterThan' references/",
  "Consider adding verification step to skill-creator checklist"
]
```

## Preserve Entries

Use "preserve" to signal content that should **not** be changed. This is just as important as identifying problems.

### What to Preserve

- Examples used verbatim without modification
- Sections that saved significant time
- Clear, immediately applicable guidance
- Perfect balance of detail
- Effective organization/structure

### Good Preserve Examples

✅ "Quick start template in SKILL.md - used as-is, saved setup time"
✅ "Single-shift pattern example - clear, concise, immediately applicable"
✅ "TESTING.md structure with Known Issues section - excellent organization"
✅ "Three-level progressive disclosure - perfect for context management"

### Avoid Vague Praise

❌ "SKILL.md was good"
❌ "Examples were helpful"
❌ "Overall well written"

Be specific about **what** worked and **why**.

## Common Pitfalls

### Don't Include

❌ Line numbers (hard for agent to reliably determine)
❌ Timestamps (agent doesn't track real-time)
❌ Speculative improvements (stick to observed issues)
❌ Personal preferences unrelated to task effectiveness

### Do Include

✅ Observable facts about what broke or worked
✅ Specific files/sections where issues exist
✅ Clear connection to human interventions
✅ Actionable suggestions with rationale
✅ Links between issues and impact

## Verification Tips

Before submitting feedback, ask:

1. **Specificity**: Could someone locate and fix this issue from my description?
2. **Impact**: Have I explained why this matters?
3. **Actionability**: Are my suggestions concrete enough to implement?
4. **Fairness**: Have I preserved what worked well?
5. **Accuracy**: Am I reporting observable facts, not speculation?

## Example: Complete Feedback Item

```json
{
  "id": "f1",
  "area": "accuracy",
  "severity": "critical",
  "action": "replace",
  "file": "references/CORE_CLASSES.md",
  "summary": "Duration uses wrong method name",
  "description": "Skill documentation references greaterThan() method throughout examples, but Duration class only implements moreThan(), lessThan(), and equals(). Found by checking src/DateTime/Duration.php when code broke.",
  "rationale": "Code fails immediately when calling greaterThan() - method doesn't exist. Required human intervention to identify correct method name. Affects all duration comparison examples in skill.",
  "suggestions": [
    "Replace all instances of greaterThan() with moreThan()",
    "Add grep verification: grep 'public function.*Than' src/DateTime/Duration.php",
    "Consider adding method verification step to skill update process"
  ],
  "required_intervention": true
}
```

This feedback item is:
- **Specific**: Names the wrong method and correct one
- **Detailed**: Explains how the error was discovered
- **Impactful**: Clear consequence (code breaks)
- **Actionable**: Concrete suggestions including verification
- **Verified**: Links to actual source file for confirmation
