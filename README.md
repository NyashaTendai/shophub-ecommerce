\# ShopHub



A small e-commerce API built to demonstrate a complete cloud delivery workflow: containerised app, infrastructure as code, automated tests and a keyless CI/CD pipeline, running on Google Cloud at near-zero cost.



\*\*Live:\*\* https://shophub-i7hqueeccq-uc.a.run.app

\- `/health` health check

\- `/api/products` product list

\- `/api/products/<id>` single product



\## Architecture



```mermaid

flowchart LR

&#x20;   Dev\[Developer] -->|git push| GH\[GitHub]

&#x20;   GH --> CI\[GitHub Actions]

&#x20;   CI -->|1. pytest| CI

&#x20;   CI -->|2. build + push image tagged with commit SHA| AR\[Artifact Registry]

&#x20;   CI -->|3. deploy, authenticated via Workload Identity Federation| CR\[Cloud Run]

&#x20;   AR --> CR

&#x20;   SM\[Secret Manager] -->|DATABASE\_URL| CR

&#x20;   CR --> DB\[(Neon PostgreSQL)]

&#x20;   User\[Visitor] --> CR

```



\## Stack



| Layer | Choice |

|---|---|

| App | Python, Flask, SQLAlchemy, Flask-Migrate, gunicorn |

| Database | PostgreSQL on Neon (free tier) |

| Container | Docker, Artifact Registry |

| Hosting | Google Cloud Run (scales to zero) |

| Infrastructure as code | Terraform (separate repo: shophub-infra) |

| CI/CD | GitHub Actions with Workload Identity Federation |

| Secrets | Google Secret Manager |



\## How it works



1\. Every push to `main` runs the test suite.

2\. If tests pass, the image is built, tagged with the commit SHA and pushed to Artifact Registry.

3\. Cloud Run is updated to that exact image, then a smoke test calls `/health`.

4\. Pull requests run tests only and never deploy.



\## Decisions and trade-offs



\- \*\*Cloud Run instead of GKE.\*\* The app is small and stateless. Cloud Run scales to zero, so an idle portfolio project costs nothing. GKE would add a cluster fee and always-on nodes.

\- \*\*Neon instead of Cloud SQL.\*\* Cloud SQL bills hourly even when idle. Neon's free tier keeps the data layer free, and it is still real PostgreSQL.

\- \*\*No stored cloud keys.\*\* GitHub authenticates to Google Cloud with short-lived tokens through Workload Identity Federation. The trust rule only accepts this repository on the `main` branch.

\- \*\*Least privilege.\*\* The deploy account can push to one registry and update one service. The runtime account can read one secret.

\- \*\*Immutable image tags.\*\* Each deploy uses the commit SHA, so every release is traceable and rollback is one command.

\- \*\*Read-only public API.\*\* There are no public write endpoints, so a public portfolio site cannot be filled with junk data. Sample products are added with a CLI command.

\- \*\*Cost controls.\*\* Max 2 instances, 512Mi memory, and a registry cleanup policy that keeps only the 2 newest images, so storage stays inside the free allowance.



\## Run locally



```bash

python -m venv venv

source venv/bin/activate        # Windows: .\\venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

flask --app app db upgrade

flask --app app seed

flask --app app run --port 8080

pytest

```



Without `DATABASE\_URL` the app uses a local SQLite file. Set `DATABASE\_URL` to a PostgreSQL connection string to use Postgres.



\## Infrastructure



Terraform code for the registry, secret, service accounts, Cloud Run service and CI/CD trust lives in the companion repo: https://github.com/NyashaTendai/shophub-infra

