# Viral Distribution Network Prototype

## Graph Schema

Nodes:
- `Creator` (creator_id, follower_count, category)
- `User` (user_id, interests)
- `Content` (content_id, topic, timestamp)

Edges:
- `FOLLOWS` (User -> Creator)
- `SHARED` (Creator -> Content, weight=probability of share)

## Example Queries

```cypher
MATCH (c:Creator)-[s:SHARED]->(cont:Content)
WHERE c.category = 'technology'
RETURN cont.content_id, avg(s.weight) as avg_share_prob
ORDER BY avg_share_prob DESC
LIMIT 10;
```

## Cascade Forecast API

`POST /api/v1/cascade`

### Request
```
{
  "content_id": "abc123",
  "initial_shares": 100
}
```

### Response
```
{
  "predicted_cascade_size": 12500,
  "top_creators": ["creator_1", "creator_7", "creator_42"]
}
```

(This API is a placeholder; full implementation scheduled for Milestone 90.)
