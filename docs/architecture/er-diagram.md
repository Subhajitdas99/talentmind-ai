# TalentMind AI ER Diagram

The Mermaid source for the ER diagram is available at [er-diagram.mmd](er-diagram.mmd).

## Relationship explanations

- Users to Recruiters: one-to-one. A user can have one recruiter profile, and each recruiter profile belongs to one user.
- Users to Candidates: one-to-one. A user can have one candidate profile, and each candidate profile belongs to one user.
- Users to Search History: one-to-many. A user can issue many searches, and each search record belongs to one user.
- Candidates to Resumes: one-to-many. A candidate can have many resumes, and each resume belongs to one candidate.
- Candidates to Candidate Skills: one-to-many. A candidate can have many skill entries, and each skill entry belongs to one candidate.
- Candidates to Embeddings: one-to-many. A candidate can have many embeddings, and each embedding belongs to one candidate or other target entity.
- Candidates to Ranking Results: one-to-many. A candidate can appear in many ranking results, and each ranking result belongs to one candidate.
- Recruiters to Jobs: one-to-many. A recruiter can create many jobs, and each job belongs to one recruiter.
- Jobs to Job Skills: one-to-many. A job can require many skills, and each job skill record belongs to one job.
- Jobs to Embeddings: one-to-many. A job can have many embeddings, and each embedding belongs to one job.
- Jobs to Ranking Results: one-to-many. A job can produce many ranking results, and each ranking result belongs to one job.
- Skills to Candidate Skills: one-to-many. A skill can be attached to many candidate skill records, and each candidate skill record points to one skill.
- Skills to Job Skills: one-to-many. A skill can be required by many job skill records, and each job skill record points to one skill.

## Notes

- The diagram uses UUID-based primary keys for all entities.
- Soft-delete fields are present on each entity but omitted from the compact diagram for readability.
- The model uses junction-style association tables for candidate and job skill links so the schema remains normalized and extensible.
