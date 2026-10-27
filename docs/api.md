# OnboardPilot API

Base URL: `http://localhost:8000` (dev). All `/api/*` routes require `Authorization: Bearer <token>` except `/api/auth/login`. `/api/public/*` and `/health` are open.

## Auth
- `POST /api/auth/login` body `{username, password}` -> `{access_token, token_type, role, full_name}`
- `GET /api/auth/me` -> current user

Roles: `it_admin`, `manager`, `employee`. Demo users: admin/Admin123!, manager/Manager123!, employee/Employee123!.

## Cases
- `GET /api/cases?status=&role_template=`
- `POST /api/cases` body `{employee_name, employee_email?, role_template, department?, start_date, manager_name?, manager_email?}`
- `GET /api/cases/{id}`
- `PATCH /api/cases/{id}`
- `DELETE /api/cases/{id}`
- `GET /api/cases/{id}/checklist` -> list items
- `GET /api/cases/{id}/handover.pdf` -> PDF

## Checklist
- `PATCH /api/checklist/{id}` body `{status, ...}` (dependency-enforced)
- `POST /api/checklist/{id}/reopen`
- `POST /api/checklist/{id}/assign` body `{owner}`

## Hardware
- `GET /api/hardware?case_id=`
- `POST /api/hardware`
- `PATCH /api/hardware/{id}`
- `DELETE /api/hardware/{id}`

## Access
- `GET /api/access?case_id=`
- `POST /api/access` body `{case_id, access_type, requester?, notes?}`
- `PATCH /api/access/{id}` body `{status, approver?, provisioning_owner?, notes?}` (state machine: requested->approved->provisioned->verified)

## Open items
- `GET /api/open-items?case_id=`
- `POST /api/open-items`
- `PATCH /api/open-items/{id}`
- `DELETE /api/open-items/{id}`

## Audit
- `GET /api/audit?case_id=&limit=`

## Guides
- `GET /api/guides?q=`
- `GET /api/guides/{slug}`

## Dashboard
- `GET /api/dashboard/summary`

## Templates
- `GET /api/templates`

## Public (read-only)
- `GET /api/public/demo`
- `GET /api/public/guides?q=`

## Health
- `GET /health`
