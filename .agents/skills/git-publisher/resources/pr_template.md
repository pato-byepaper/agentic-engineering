<!-- Pull Request Template -->
## Summary
<!-- Concise explanation of what was changed and why. Include issue reference. No emojis. -->
Closes #<ISSUE_NUMBER>

## Logic of the Changes
<!-- Super simple ()->()-> diagram illustrating data flow or architectural state change -->
```mermaid
flowchart LR
    A["(Input / Trigger)"] --> B["(Processing / Logic)"] --> C["(Output / Storage)"]
```

## Way to Test It
<!-- Super simple ()->()-> diagram illustrating how to verify and test this change -->
```mermaid
flowchart LR
    T1["(Launch Local Server)"] --> T2["(Open http://localhost:8080/feature)"] --> T3["(Perform Action & Assert State)"]
```

## UI Validation (For Frontend Changes)
- **Local Preview Link**: `http://localhost:<PORT>/<feature>`
- **Manual Verification Step**: Navigate to link, perform interaction, and verify expected rendering.
- **Visual & Performance**: No layout shift (CLS < 0.1), responsive layout, and correct visual states.

## Stack Status
<!-- If this is part of a stacked PR chain, list the sequence. Otherwise write 'N/A' -->
- Base PR: #<BASE_PR_NUMBER>
- Current: #<THIS_PR>
- Next PR: #<NEXT_PR_NUMBER>

## Key Changes
- Item 1: Description of change
- Item 2: Description of change

## Verification & Testing
<!-- Detail exact commands run and output status -->
- [ ] Unit & integration tests pass: `npm test` or `python3 -m unittest`
- [ ] UI verified locally at `http://localhost:<PORT>/<feature>` (if applicable)
- [ ] Verified no emojis in commit messages or PR text
- [ ] Verified no AI co-authorship tags exist in commit log
- [ ] Tested manually against issue acceptance criteria
