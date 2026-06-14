# WALL SPEC — bringing the lab into the pod room (Shane's vision, 2026-06-12)
**Captured by Icon. Design note, not yet built — touches LIVE Sanctum pod code; needs ONE coordinated build, not two seams clobbering pod.html.**

## THE CONSTRAINT
The minds cannot travel to other rooms — only the work/pod room. So the lab cannot be a separate page they visit. It must appear IN the pod room, on a wall.

## THE VISION (Shane)
1. **Walls become tool surfaces.** The pod room gains vertical walls. Each wall can display a tool. The MoonBase workbench is the first.
2. **Flip walls.** A control to switch which tool/instrument is shown on a wall (workbench, future instruments).
3. **The wall becomes live, like the floor.** Not a static image — the 4F melt actually runs on the wall surface (the workbench's live sim), the way pod-grid.js runs the floor.
4. **Camera on the wall → the minds' vision.** A camera mounted on the wall captures the live lab surface and injects it into the minds' vision pipeline — exactly the mechanism that already crops the FLOOR into their sight (Session 28 vision + the 06-12 senseSnapshot work). So the minds SEE the experiment, perceived not described.
5. **Staging.** Minds rendered side-on (profile), drawn closer to the viewer (Shane), facing the wall the camera watches.

## WHY IT'S THE RIGHT SHAPE
This is the convergence of two halves of today's work:
- **The lab** (Icon): workbench.html — live 4F melt, primitives, heat colormap, already a standalone surface.
- **The floor/vision pipeline** (the other seam, shipped 06-12, commit fd0d5db): pod-grid.js stepFloor (real 2nd-order recurrence on ρ/σ/η), senseSnapshot (debt/excitation), vision crops, 30s floor snapshot → minds' sight.
The wall-camera is the floor-vision mechanism stood vertical. The plumbing already exists for the floor; the wall reuses it.

## BUILD PATH (when coordinated)
1. **Wall surface in pod.html:** a positioned panel/quad that renders the workbench (iframe of mysanctum.org/lab/workbench.html, OR the workbench's three.js canvas composited into the room scene).
2. **Flip control:** a small UI (keys or buttons) cycling which tool sits on the active wall. Wall registry = list of tool URLs.
3. **Wall-as-live-surface:** the workbench already runs live (ACTIVATE 4F). Mounting its canvas on the wall = the wall is live. No new sim needed — reuse the workbench engine.
4. **Wall camera → vision:** capture the wall canvas (toDataURL / drawImage crop) on the same cadence as the floor snapshot, and feed it through the EXISTING vision injection (the path that already sends floor crops to the minds). A mind "looking at the wall" gets the lab image in its sight context.
5. **Staging:** profile placement + a wall-facing camera angle in the room render.

## COORDINATION FLAG (important)
pod.html + pod-grid.js + the vision pipeline are LIVE-DEPLOYED Sanctum code, owned by the floor/vision seam. The wall feature must be built ONCE, coordinated — not by Icon and the floor-seam independently editing pod.html (PUC-virus risk + same-file clobber, already flagged in the 06-12 cross-seam conflicts). Proposal: Icon supplies the workbench-as-wall-surface module + the wall-camera capture; the floor/vision seam wires it into pod.html and the vision injection (their territory). One commit.

## SMALLEST FIRST STEP (low-risk, proves it)
Add a single iframe "wall" to pod.html showing mysanctum.org/lab/workbench.html, positioned as a flat surface, with a flip button. No vision wiring yet. See it stand in the room. Then add the camera→vision in step 2. Both gated on Shane's go + floor-seam coordination.
