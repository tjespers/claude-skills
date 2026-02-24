---
name: meeting-note-taker
description: Transform meeting transcripts into structured, decision-oriented meeting notes. Use when a user provides a meeting transcript (Google Meet + Gemini, or other supported formats) and wants structured notes with agenda, discussion summaries, decision log, and action items. Triggers include "take notes from this transcript", "create meeting notes", "process this meeting", or when a user provides a transcript file for summarization.
metadata:
  version: 1.0.0
  author: Tim Jespers <git@tjespers.dev>
  license: Apache-2.0
---

# Meeting Note Taker

Transform a meeting transcript into structured, decision-oriented meeting notes. The output captures what was discussed, what was decided, and what needs to happen next — optimized for async consumption by participants who were present and stakeholders who were not.

## Hard Constraints

1. **Fidelity over brevity.** Do not omit decisions, action items, or disagreements to make notes shorter. Every decision made in the meeting must appear in the decision log.
2. **Zero fabrication.** Do not invent decisions, action items, or discussion points that did not occur. If a topic was mentioned but not resolved, capture it as an open item, not a decision.
3. **Attribute accurately.** When a participant proposes something, is assigned a task, or makes a key argument, attribute it correctly. Do not guess attribution — if unclear, use passive voice.
4. **Preserve terminology.** Use the same terms participants used. Do not normalize, correct, or improve domain-specific language. If participants said "constraint provider," write "constraint provider."
5. **Decisions require explicit agreement.** Only log something as a decision if participants explicitly agreed. Silence or moving on is not agreement — flag unresolved topics as open items.
6. **Sequential numbering is stable.** Discussion items, decisions (D1, D2...), and tasks (T1, T2...) are numbered sequentially and referenced by these IDs throughout the document. IDs must not change if the document is later amended.

## Transcript Types

Each supported transcript format has a dedicated reference file in `references/` describing its structure. When processing a transcript, first identify which format it matches, then follow the parsing rules for that format.

### Supported formats

| Format | Reference | Structure |
|--------|-----------|-----------|
| Google Meet + Gemini | [`references/google-meet-gemini.md`](references/google-meet-gemini.md) | Gemini-generated summary + notes + timestamped speaker turns |

When a transcript does not match any supported format, inform the user and ask them to provide a reference example for the new format before proceeding.

## Input

The user provides one of:

- A **file path** to a transcript document
- A **pasted transcript** directly in chat
- A **URL** to a transcript (if the tool environment supports fetching)

Optionally, the user may also provide:

- **Meeting type** (e.g., "spec shaping", "sprint planning", "design review") — used in the YAML frontmatter `type` field. If not provided, infer from content or ask.
- **Participant roles** — if known. If not provided, infer from the transcript where possible (e.g., who presents vs who questions) or set to `"unknown"`.
- **Spec or feature context** — if the meeting relates to a specific spec or feature, the user may provide a reference. This helps with accurate terminology and context extraction.

## Output

A single Markdown document following the template at [`templates/meeting-notes.md`](templates/meeting-notes.md).

### Output location

- **Default:** Write to file. Ask the user where to store it.
- **Naming convention:** `YYYYMMDD-<type>.md` (e.g., `20260223-shaping.md`)
- **Suggested locations:** If a spec folder is identifiable from context, suggest `specs/<spec-folder>/meeting-notes/`. Otherwise, ask the user.

### Output structure

The template defines five sections. Each has specific extraction rules:

#### 1. YAML Frontmatter

Populate from transcript metadata and user input:

- `type` — meeting type (from user input or inferred)
- `date` — meeting date (from transcript metadata)
- `spec` — spec ID if applicable (from user input or inferred from discussion content)
- `spec_folder` — spec folder path if applicable
- `artifact` — spec artifact under discussion if applicable
- `participants` — extracted from transcript speaker labels; roles from user input or inferred
- `decisions` — total count of decisions in the decision log (populated after extraction)
- `tasks` — total count of tasks in the action items table (populated after extraction)

#### 2. Agenda

A numbered list of discussion topics, each linking to its discussion section. Extract topics by identifying:

- Explicit agenda items mentioned at the start of the meeting
- Natural topic transitions during conversation (speaker says "next point", "moving on to", or starts discussing a new subject)
- Topics that were added during the meeting (mark with "Added during session")

If topics were discussed out of order or merged, reflect the actual discussion order, not the original agenda order. Note merges explicitly.

#### 3. Discussion & Decisions

One subsection per agenda item. For each, extract:

**Context** — What is the topic about? What prompted the discussion? Extract from the initial framing or opening statement on the topic.

**Discussion** — Summarize the substance of the conversation:
- What positions or perspectives were shared?
- What trade-offs were considered?
- What examples or evidence were cited?
- Where did participants disagree before converging?

Keep it concise but complete. A reader who missed the meeting should understand not just WHAT was decided but WHY.

**Follow-up** — Link to tasks (T1, T2...) from the action items table that were identified during this specific discussion. Omit this field if no follow-ups were identified for this topic.

**Decisions** — Link to decisions (D1, D2...) from the decision log that resulted from this discussion. Every discussion item should produce at least one decision. If a topic was discussed but not resolved, note it as an open item and create a task for resolution.

#### 4. Decision Log

A quick-reference table with:

| Column | Content |
|--------|---------|
| `#` | Sequential ID: D1, D2, D3... |
| `Topic` | Link to the discussion section where this decision was made |
| `Decision` | One-line summary of what was decided. Must be actionable and unambiguous. |

Extraction rules:
- A decision is an explicit agreement to do or not do something
- "Let's go with X" followed by agreement = decision
- "We should think about X" without resolution = NOT a decision (capture as open item / task)
- Number decisions in the order they were made, not by topic order

#### 5. Action Items

A task table with:

| Column | Content |
|--------|---------|
| `#` | Sequential ID: T1, T2, T3... |
| `Source` | Link to the discussion topic that spawned this task. Use `—` if the task is general (e.g., "schedule next meeting"). |
| `Task` | Single-line description of what needs to happen |
| `Assignee` | Who will do this — use the participant's name or role (e.g., "domain expert", "spec writer", "roadmap manager"). If unassigned, write `unassigned`. |

Extraction rules:
- Explicit assignments ("I'll do X", "Can you handle Y?") = task with assignee
- Implicit next steps ("We need to X before next meeting") = task, assignee from context or `unassigned`
- Do not create tasks for completed in-meeting actions

## Processing Procedure

### Phase 1: Parse transcript

1. Identify the transcript format by matching against supported formats in `references/`.
2. Extract metadata: date, time, participants, duration.
3. Parse speaker turns with timestamps (format-specific).
4. If the transcript includes a Gemini-generated summary, read it for orientation but do NOT use it as the primary source — always extract from the full transcript.

### Phase 2: Identify structure

1. Read the full transcript end-to-end before extracting anything.
2. Identify topic boundaries — where does discussion shift from one subject to another?
3. Build the agenda from identified topics.
4. Note which participants are most active on which topics (helps with role inference and attribution).

### Phase 3: Extract per topic

For each identified topic:

1. Identify the opening framing → **Context**
2. Trace the discussion flow: positions stated, trade-offs weighed, examples given, convergence reached → **Discussion**
3. Identify explicit agreements → candidate **Decisions**
4. Identify next steps or assignments → candidate **Tasks**
5. Identify cross-references to other topics → **Follow-up** links

### Phase 4: Compile and cross-reference

1. Number all decisions sequentially (D1, D2...).
2. Number all tasks sequentially (T1, T2...).
3. Add decision and task links to each discussion section.
4. Populate YAML frontmatter counts.
5. Verify: every decision links back to a discussion topic, every task links to a source.

### Phase 5: Write output

1. Apply the template from `templates/meeting-notes.md`.
2. Write the file to the agreed location.
3. Report: file path, number of discussion topics, decisions, and tasks extracted.

## Edge Cases

- **Crosstalk or unclear attribution**: Use passive voice ("It was suggested that...") rather than guessing who said what.
- **Off-topic tangents**: Include only if they produced a decision or action item. Otherwise omit.
- **Unresolved disagreements**: Capture both positions in the Discussion summary. Do NOT log a decision. Create a task: "Resolve [topic] — positions: [A] vs [B]."
- **Action items without clear assignees**: Log with `unassigned`. Do not guess.
- **Very long meetings (>60 min)**: Process in topic-sized chunks. Do not attempt to hold the entire transcript in working memory at once.
- **Non-English transcripts**: Preserve the original language for terminology and quotes. Write structural elements (section headers, column labels) in English.
- **Multiple meetings in one transcript**: Ask the user to clarify scope or split into separate notes documents.
