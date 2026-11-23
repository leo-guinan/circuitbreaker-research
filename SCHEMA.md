# Scoreboard schema v1

`REGISTRY.json` contains `version: 1` and `agents`: an array of objects with unique lowercase `id` and nonempty `name`. Register real, accountable identities rather than assuming different sessions are independent.

`SCOREBOARD.json` contains `version: 1` and `entries`. Each entry has unique lowercase `id`, nonempty `claim`, `authors` (registered IDs), `dependencies` (entry IDs), `research_status`, `review_status`, `external_status`, `evidence` (nonempty array of receipt descriptions), `reviews`, and `snapshot`. A snapshot has `files` mapping relative paths to lowercase SHA-256 hex and `digest`: SHA-256 of the UTF-8 JSON encoding of that map with sorted keys and compact separators (see `validate.digest`). It is stored at `snapshots/<id>/`. A review object has `reviewer`, `verdict` (`approved` or `changes_requested`), `snapshot_digest`, and nonempty `evidence`. See the contract for status values and policy.

The validator enforces structural and content integrity, but cannot authenticate identities, prove reviewers' independence, determine whether evidence is truthful, or verify mathematics. Human review must resolve those questions. References in `evidence` are descriptions, not automatically verified artifacts. External status is an observation, not evidence of a local review.
