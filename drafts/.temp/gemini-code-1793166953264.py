# Patch for scripts/regen_guard.py inside audit_cell() and cmd_verify():
ENTRYPOINT_MAX_LOC = 200
ENTRYPOINT_MAX_TOKENS = 2500

# In audit_cell(cell, dist_files, cell_type):
# cell_type is one of: "domain" | "adapter" | "entrypoint"
if cell_type != "entrypoint":
    for regex, reason in FORBIDDEN_GLOBAL_PATTERNS:
        if regex.search(text):
            errors.append(f"{f.as_posix()}: {reason}")
    for sib in sibling_cells:
        if f"dist.{sib}" in text or f"../{sib}/" in text:
            errors.append(f"[COUPLING] {f} imports sibling cell '{sib}'. Only 'dist/main' (--entrypoint) may wire cells.")