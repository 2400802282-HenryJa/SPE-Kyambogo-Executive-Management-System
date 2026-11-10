# SPE Kyambogo Executive Management Information System (SK-EMIS)

A web-based platform for managing the activities, projects, programmes, resources and accountability of the **Society of Petroleum Engineers (SPE) Kyambogo University Student Chapter** executive.

> **Guiding principle:** Every initiative must produce a measurable outcome for SPE Kyambogo. The system makes it easy to see what has been done, who is responsible, what resources were used and what remains outstanding.

**Status:** Early development (pre-v0.1). Not yet in production.
**Maintainer:** Chairperson, Projects, Innovation and Resources Development.

---

## 1. Purpose

Chapter executives currently coordinate through scattered chats, spreadsheets and memory. SK-EMIS digitises a process that already works; it is not meant to add bureaucracy. It gives the executive one place to:

- track projects, owners, milestones and deadlines;
- plan programmes and events and record follow-up actions;
- keep a shared directory of experts, partners and schools;
- account for merchandise, assets and resource mobilisation;
- submit and consolidate monthly departmental reports.

## 2. Design principles

1. **Small and modular.** Solve immediate coordination problems first; expand as the chapter grows.
2. **Follow the chapter framework.** Reporting flows from Department Head to CAO. The CAO consolidates for the President and Vice President.
3. **Single source of truth for membership.** SK-EMIS does not create competing membership records. Any membership integration is coordinated with the Membership Office and permission-controlled.
4. **Privacy and security by default.** Least-privilege access; no secrets or private member data in the repository.
5. **Continuity.** Executives change every year. Documentation and clean handover are first-class features.

## 3. Users and roles

| Role | Typical access |
|---|---|
| President / Vice President | Full read access, executive dashboard, consolidated reports |
| CAO | Read all departments, consolidate and review reports |
| Department Heads | Manage own department's projects, programmes, resources, reports |
| Authorised Officers | Limited create/update rights within assigned modules |
| Membership Office liaison | Controlled access to membership coordination data |

Roles map to Django groups and permissions. Exact permission matrix: see `documentation/permissions.md` (to be written).

## 4. Modules

| App | Responsibility | Version |
|---|---|---|
| `accounts` | Users, officers, roles, permissions | v0.1 |
| `departments` | Departments, department heads, reporting lines | v0.1 |
| `projects` | Projects, tasks, owners, milestones, deadlines, status, challenges | v0.1 |
| `programmes` | Events, attendance, volunteers, invited speakers, follow-up actions | v0.2 |
| `contacts` | Industry experts, partner organisations, schools, programme contacts | v0.2 |
| `resources` | Merchandise, stock, assets, costs, sales, resource mobilisation | v0.3 |
| `publications` | Essays, abstracts, submission status | v0.3 |
| `reports` | Departmental updates, monthly reports, outstanding tasks, executive dashboard | v0.4 |
| Membership integration | Read-only or controlled coordination with the Membership Office | Later |

## 5. Technology

| Component | Choice | Purpose |
|---|---|---|
| Backend | Python 3 + Django | Application logic, authentication, permissions, admin |
| Database | SQLite (development), PostgreSQL (deployment) | Chapter records |
| Frontend | Django templates + Bootstrap | Clean, responsive interface |
| Reporting | Python + Pandas | Summaries and CSV/Excel exports |
| Version control | Git + GitHub | Source, collaboration, documentation |
| Deployment | To be decided | Online access for executives |

## 6. Repository structure

```
spe-kyambogo-emis/
├── config/            # Django project settings and URLs
├── accounts/          # Users, roles, permissions
├── departments/       # Departments and reporting lines
├── projects/          # Projects, tasks, milestones
├── programmes/        # Events and participation
├── contacts/          # Experts and stakeholders
├── resources/         # Merchandise, assets, finances
├── publications/      # Essays and abstracts
├── reports/           # Monthly accountability and dashboard
├── templates/         # Shared HTML templates
├── static/            # CSS, JS, images
├── documentation/     # Requirements, design, handover notes
├── tests/             # Automated tests
├── manage.py
├── requirements.txt
├── .env.example       # Template for environment variables (no real values)
├── .gitignore
└── README.md
```

## 7. Getting started (local development)

**Prerequisites:** Python 3.11+, Git.

```bash
# 1. Clone
git clone https://github.com/2400802282-HenryJa/SPE-Kyambogo-Executive-Management-System.git
cd SPE-Kyambogo-Executive-Management-System

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env      # then edit .env with your own values

# 5. Set up the database and an admin account
python manage.py migrate
python manage.py createsuperuser

# 6. Run
python manage.py runserver
```

Open http://127.0.0.1:8000/.

> The commands above apply once the Django project has been scaffolded (see Roadmap, Phase 0).

## 8. Security rules (mandatory)

- **Never commit** passwords, `SECRET_KEY`, database credentials, API keys, or private member information.
- Keep secrets in environment variables (`.env` is git-ignored).
- Do not upload real member lists, phone numbers or financial records to GitHub. Use fictional sample data for development and tests.
- Keep `DEBUG = False` in any deployed environment.
- Grant repository access only to people who need it. **Prefer a private repository** while the system holds anything beyond source code.
- Review who has access at every executive handover.

## 9. Working routine the system supports

| Activity | Frequency | Expected output |
|---|---|---|
| Team coordination | Weekly | Updates and agreed actions |
| Project follow-up | Weekly | Progress and outstanding tasks |
| Resource and merchandise updates | As transactions occur | Updated resource records |
| Programme and stakeholder contact updates | After each engagement | Updated contact database |
| Departmental accountability | Monthly | Report to the CAO |
| Visibility and outreach | Ongoing | Evidence of engagement |

## 10. Roadmap

- **Phase 0 – Foundation:** scaffold Django project, set up apps, `.gitignore`, `requirements.txt`, `.env.example`; write requirements and permission matrix.
- **Phase 1 – v0.1:** executive/user management, departments, project tracking, basic dashboard.
- **Phase 2 – v0.2:** programmes and contacts.
- **Phase 3 – v0.3:** resources, merchandise and publications.
- **Phase 4 – v0.4:** monthly reports, outstanding-task views, executive dashboard, exports.
- **Phase 5:** migrate to PostgreSQL, choose hosting, backups, controlled membership integration.

## 11. Contributing

1. Create a branch from `main`: `feature/<short-description>`.
2. Keep commits small with clear messages.
3. Add or update tests for new behaviour.
4. Open a pull request. Another contributor reviews before merging.
5. Document any change to roles, permissions or data handling.

## 12. Documentation

Planned files in `documentation/`: `requirements.md`, `permissions.md`, `data-model.md`, `deployment.md`, `handover.md`.

## 13. Licence and ownership

This is an internal chapter system. Licence and ownership to be agreed with the chapter executive and, where required, the University and SPE. Until then, all rights reserved.

---

*SPE Kyambogo Executive Management Information System: making chapter work visible, accountable and continuous.*
