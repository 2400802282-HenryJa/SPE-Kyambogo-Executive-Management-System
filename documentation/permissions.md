# Permissions (v0.4)

## Roles
| Role | How it is set | Access |
|---|---|---|
| Developer | Django superuser | Everything, including admin privilege settings |
| President, Vice President, CAO ("top executives") | `position` on the user | Everything in the chapter system (view and edit); Admin site access, but cannot change privilege flags or touch superusers |
| Treasurer | `position` = Treasurer | Treasury/finance records (module not built yet) plus own department |
| Department Head | `Department.head` | Their department, plus adding and removing department members |
| Other executives | Added to a department by its head | View and work within their own department(s) only |

## Rules
- **Admin site** is only for the developer and the three top executives. This is enforced automatically: a user's `is_staff` flag is set from their position every time they are saved.
- **Projects:** visible to members and head of the project's department, the project owner, anyone assigned a task in it, and top executives. Others get "not found".
- **Programmes and events:** visible to every logged-in user. Edited by the coordinator, the department head or a top executive.
- **Contacts:** President, VP, CAO and developer only. Other coordinators can still add an invited speaker to a programme by typing the name.
- **Resources catalogue and stock levels:** visible to every logged-in user. Items, stock movements and sales are recorded by top executives and the owning department's head and members.
- **Cost prices, revenue and net figures:** only the Treasurer, top executives, developer and the owning department's head.
- **Resource mobilisation (donations/sponsorship):** only the Treasurer, top executives, developer, and department heads (for their own department).
- **Treasury/finance:** confidential. Use `TreasuryAccessMixin` (accounts/mixins.py) on every finance view: only Treasurer, President, VP, CAO and the developer.
- **Department members** are managed on the Departments page by the head (or a top executive).
- After changing roles in bulk, run `python manage.py sync_roles`.
