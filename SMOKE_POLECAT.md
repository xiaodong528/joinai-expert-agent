# Smoke Test — Polecat Dispatch Validation

**Created:** 2026-04-11T02:55:04Z  
**Polecat:** rust  
**Rig:** sp_smoke  

This file validates the full bead → Polecat dispatch chain:  
Mayor dispatches bead → Witness assigns to Polecat → Polecat picks up hook → Polecat creates artifact → Polecat submits via `gt done`.
