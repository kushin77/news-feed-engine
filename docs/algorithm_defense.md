# Algorithm Hacking Defense Rules

This document lists detection rules and mitigation strategies to prevent
malicious actors from gaming the recommendation algorithm.

## Detection Rules

1. **Session Frequency Spike**: more than 500 ranking requests from same IP/user
   within 1 minute.
2. **Similarity Flood**: same user requesting identical content permutations
   >10 times in 5 minutes.
3. **Creator Collaboration Loop**: small set of creators repeatedly liking each
   other's content more than expected given baseline engagement.

When a rule triggers, throttle the user for 1 hour and send alert to security
team.

## Mitigation Actions

- Temporary account suspension
- Manual review of affected content
- Rate limiting at the API gateway

(Milestone 89 deliverable: rule set defined; rule engine stub will be
implemented in future milestone.)