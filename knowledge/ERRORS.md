# Errors

Record deterministic errors, root causes, and fixes here.

## 2026-11-08 — Store listing cache after release

A new release and previews were visible in the hydrated listing while direct listing HTML still returned 0.1.1. Switching devices in an already open browser tab also briefly showed the previous preview set. Verify through a fresh navigation for each selected device, then compare the rendered gallery order and download link to the public asset bytes. The update path is recorded in execution/publish_route_update.py.
