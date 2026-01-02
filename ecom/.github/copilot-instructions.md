# Copilot instructions for Job House (ecom)

Purpose
- Help AI coding agents make focused, safe edits in this Django app (Job House).

Big picture
- Small Django 6 project with a custom `CustomUser` model (not using `django.contrib.auth`) and session-based auth: see `ecom/store/models.py` and `ecom/store/decorators.py`.
- Key domains: `Profile` (user profile + uploads), `Job` listings, `JobApplication` (one application per user/job). Uploaded files live under `media/` (profiles/ and resumes/).

Key files to read before changing behavior
- `ecom/ecom/settings.py` — email SMTP config, `STATICFILES_DIRS`, and `MEDIA_ROOT`.
- `ecom/store/models.py` — `CustomUser`, `Profile`, `Job`, `JobApplication` (note: `JobApplication.resume` uploads to `leatest_resumes/` — a literal folder name used by the project).
- `ecom/store/views.py` — primary app logic (session usage, OTP flows, `apply_job` returns JSON; email is sent here).
- `ecom/templates/dashboard.html` — job cards, `apply` button, popup markup, and a hidden `csrfmiddlewaretoken` input used by front-end code.
- `ecom/static/js/Dashboard.js` — client-side behaviors (popup, apply request). Modify carefully to preserve CSRF handling.

Project-specific conventions & patterns
- Authentication: custom password hashing with `bcrypt` and manual `request.session['user_id']`. Do NOT switch to `django.contrib.auth` without full migration plan.
- Session guard: `@session_login_required` decorator protects many views; update or reuse it for new endpoints that require login.
- Email: settings contain real SMTP credentials (in `settings.py`) — treat as secrets; do not commit new secrets. For local testing, prefer console email backend.
- File uploads: templates reference `profile.profile_image.url` and `profile.resume.url`. Ensure `MEDIA_ROOT` is configured and `MEDIA_URL` is served in dev.
- Frontend–backend contract: `apply_job` expects a POST and returns JSON (status: `success` | `incomplete` | error). Dashboard UI calls this via JS.

Common workflows / commands
- Create / activate venv (Windows):
  - `env\\Scripts\\activate` then `python manage.py migrate` and `python manage.py runserver`
- Send migrations / DB:
  - `python manage.py makemigrations` (if models change)
  - `python manage.py migrate`
- Static & media during development: `STATICFILES_DIRS` points to `static/`; `MEDIA_ROOT` → `media/`. Use Django dev server to serve media or configure urls accordingly.

Safe-edit guidance for agents
- When changing authentication or password handling, respect existing `bcrypt` usage and session-based login; document migration steps if altering.
- When adding endpoints consumed by `Dashboard.js`, keep responses JSON-shaped as existing code expects; preserve HTTP status codes used by the client.
- For file-upload fields, reference `Profile.resume.url` and `JobApplication.resume` path (`leatest_resumes/`) — tests or fixes may need to rename the folder consistently.
- Avoid hardcoding secrets; use environment variables for credentials and update `settings.py` only with a migration comment.

Examples
- To open the apply popup: `ecom/templates/dashboard.html` uses `<button onclick=\"openApplyPopup({{ job.id }})\">` and the JS in `ecom/static/js/Dashboard.js` handles the POST to the `apply_job` view.
- `apply_job` view (in `ecom/store/views.py`) returns `JsonResponse({"status":"incomplete", "message": ...})` when profile incomplete — client-side UI expects that message.

If unsure
- Run the dev server and reproduce the UI flow before changing both front-end and view logic:
  - `env\\Scripts\\activate`
  - `python manage.py runserver`
- Ask the maintainer whether it is acceptable to modify authentication or storage paths; these are cross-cutting.

Please review and tell me if you want this file extended with quick code examples (patches) to implement any targeted change (e.g., reopen apply modal after profile save, or standardize resume upload folder name).
