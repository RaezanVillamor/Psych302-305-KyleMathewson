# PSYCH 302 / 305 Canvas pipeline

Private instructor tool. Token lives in `Psych275_Instructor/pipeline/.env` (same Canvas account). This folder overrides the course id to **35483**.

```bash
cd /Users/kylemathewson/Teaching/PsychCompute302-305/pipeline
source /Users/kylemathewson/Teaching/Psych275_Instructor/pipeline/.venv/bin/activate
python studio_pipeline.py courses
python studio_pipeline.py week0-create
# after students submit:
python studio_pipeline.py week0-pull
```

`week0-pull` writes `out/week0_roster.json`: Canvas user ↔ GitHub username, Education status, repo consent. That file is the input for minting 50 private studio repos later.

To the agent: **`plant week0`** means create (or confirm) the assignment and announcement. **`pull week0`** means harvest usernames.
