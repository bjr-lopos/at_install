# Project guidance for Claude

## Commit policy
- **Never** add a `Co-Authored-By: Claude ...` trailer (or any Claude/AI co-author line) to commit messages. Commit messages must contain no AI attribution.

## Deployment note
- The running services execute copies under `/usr/local/bin` (`loposScheduler.py`, `loposPyLib.py`, `loposTDoA2Pos.py`, `loposcore`), installed by `bootstrap.sh` via `sudo cp`. A `git pull` into the working dir does **not** update them — you must `sudo cp` the changed files to `/usr/local/bin` and restart the services (`loposcore`, `loposmath`/`lms`, `loposplan`). The scheduler also imports `localConfig` from `/usr/local/bin` when launched from there.
