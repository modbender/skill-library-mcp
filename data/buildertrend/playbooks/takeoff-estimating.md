# Buildertrend Takeoff — Digital Plan Measurement (Agent-Assisted)

## Overview
Buildertrend Takeoff is an integrated digital measurement tool for blueprints and construction plans. Upload PDFs, calibrate scale, measure linear distances, areas, and counts, then assign quantities directly to estimate line items and cost codes. This creates a seamless pipeline: **Takeoff → Estimate → Proposal → Budget**.

## Trigger
- the user says "do a takeoff for [project]", "measure plans", "upload blueprints"
- New plans/blueprints received for estimating
- Estimate needs quantity verification from plans
- "Launch takeoff from estimate"
- procurement agent requests measurements for a procurement quote

---

## Step 1: Navigate to Plans & Takeoff
**Action:** Open Plans page or launch from Estimate

### From Plans & Specs
```
browser → navigate to https://buildertrend.net/app/Plans
browser → snapshot → verify Plans page loaded
```

**URL:** `/app/Plans`
**Tabs:** Plans | Specs

### From Estimate (Recommended)
```
browser → navigate to https://buildertrend.net/app/Estimate
(select job first)
browser → snapshot → click "Launch Takeoff" in toolbar
browser → snapshot → verify Takeoff interface loaded
```

### Takeoff Settings
**URL:** `/app/Settings/TakeoffSettings`

---

## Step 2: Upload Plans/Blueprints
**Action:** Upload PDF blueprints for digital takeoff

```
browser → snapshot → click "Create new Plan" or "Upload" button
browser → snapshot → select PDF file(s) from computer
browser → snapshot → wait for upload and processing
browser → snapshot → verify plans appear in plan list
```

**Supported formats:** PDF (primary), image files
**Best practices:**
- Upload full plan sets (all sheets)
- Name files clearly: `A-101 Floor Plan`, `S-201 Structural`, etc.
- Organize by discipline: Architectural, Structural, MEP, etc.

**Message to the user:**
```
📐 Plans uploaded for [project]:
• Files: [count] sheets
• Sheets: [list of sheet names]
• Ready for takeoff measurement
```

---

## Step 3: Scale Calibration
**Action:** Set the measurement scale on each plan sheet

### Why Calibration Matters
Digital plans need a known reference dimension to convert screen pixels to real-world measurements. Without calibration, all measurements will be wrong.

### Calibration Steps
```
browser → snapshot → open a plan sheet in Takeoff
browser → snapshot → click "Calibrate Scale" tool
browser → snapshot → find a known dimension on the plan (e.g., a wall labeled "10'-0"")
browser → snapshot → click start point of the known dimension
browser → snapshot → click end point of the known dimension
browser → snapshot → enter the known length (e.g., 10 ft)
browser → snapshot → click "Apply" / "Save"
browser → snapshot → verify scale indicator shows correct ratio
```

**Tips:**
- Use longest known dimension available for best accuracy
- Re-calibrate if plan was printed at different scale
- Check calibration by measuring another known dimension
- Each sheet may need separate calibration if scales differ

---

## Step 4: Digital Takeoff Tools

### Linear Measurement
**Use for:** Walls, baseboards, crown molding, piping runs, conduit, framing lengths

```
browser → snapshot → select "Linear" measurement tool
browser → snapshot → click start point on plan
browser → snapshot → click through intermediate points (for turns/bends)
browser → snapshot → double-click end point to complete measurement
browser → snapshot → verify measurement appears with length value
```

### Area Measurement
**Use for:** Flooring, painting, drywall, roofing, concrete pours, tile areas

```
browser → snapshot → select "Area" measurement tool
browser → snapshot → click corners of the area to trace the boundary
browser → snapshot → close the shape (click back on first point or double-click)
browser → snapshot → verify measurement shows square footage
```

### Count
**Use for:** Doors, windows, outlets, fixtures, light switches, plumbing fixtures

```
browser → snapshot → select "Count" tool
browser → snapshot → click each item on the plan to count it
browser → snapshot → verify count total updates with each click
```

### Measurement Display
Each measurement shows:
- Measurement value (length, area, or count)
- Color coding by layer/category
- Label with assigned cost code
- Running total per layer

---

## Step 5: Layer Management
**Action:** Organize measurements by trade/discipline

### Layer Structure
Layers separate different measurement types for clarity:
| Layer | Color | Used For |
|---|---|---|
| Framing | Blue | Wall lengths, stud counts |
| Electrical | Yellow | Conduit runs, outlet counts |
| Plumbing | Green | Pipe runs, fixture counts |
| HVAC | Orange | Ductwork runs, vent counts |
| Flooring | Brown | Floor areas |
| Painting | Purple | Wall/ceiling areas |
| Drywall | Gray | Wall/ceiling areas |
| Demolition | Red | Demo areas, quantities |

### Managing Layers
```
browser → snapshot → find Layer panel (sidebar)
browser → snapshot → click "Add Layer" to create new
browser → snapshot → name layer and set color
browser → snapshot → toggle layer visibility on/off
browser → snapshot → switch between layers when measuring
```

**Best Practice:** Create one layer per cost code/trade to keep measurements organized.

---

## Step 6: Assign Measurements to Estimate
**Action:** Link takeoff quantities to estimate line items

### From Takeoff → Estimate
```
browser → snapshot → select completed measurements
browser → snapshot → click "Assign to Estimate" or "Export to Estimate"
browser → snapshot → select or create estimate line item
browser → snapshot → set cost code for the line item
browser → snapshot → verify quantity transferred to estimate
browser → snapshot → click "Save"
```

### Automatic Flow
When launching Takeoff from the Estimate:
1. Measurements link directly to estimate line items
2. Quantities auto-populate the estimate's quantity column
3. Unit costs × takeoff quantities = total cost per line

### Cost Code Assignment
| Measurement Type | Suggested Cost Code | Unit |
|---|---|---|
| Wall framing LF | 05.00 Carpentry / Framing | LF (linear feet) |
| Floor area SF | 15.00 Flooring & Tile | SF (square feet) |
| Paint area SF | 14.00 Painting and Coating | SF |
| Drywall area SF | 10.00 Insulation & Drywall | SF |
| Door count EA | 13.00 Windows & Doors | EA (each) |
| Window count EA | 13.00 Windows & Doors | EA |
| Outlet count EA | 08.00 Electrical | EA |
| Pipe run LF | 07.00 Plumbing | LF |
| Duct run LF | 09.00 HVAC | LF |
| Concrete area SF | 04.00 Excavation Foundation | SF/CY |
| Roofing area SF | 06.00 Roofing | SF/SQ |
| Demo area SF | 20.10 Demolition | SF |

---

## Step 7: Markup and Annotation
**Action:** Add notes, callouts, and markups to plans

```
browser → snapshot → select markup/annotation tool
browser → snapshot → choose tool type (text, arrow, circle, highlight, cloud)
browser → snapshot → click on plan to place annotation
browser → snapshot → type annotation text if applicable
browser → snapshot → save markup
```

**Markup tools typically include:**
- Text callouts
- Arrows and pointers
- Circles and rectangles
- Cloud/revision marks
- Highlights
- Freehand drawing

**Use for:** RFI references, site coordination, sub instructions

---

## Step 8: Comparison — Original vs Revised Plans
**Action:** Compare plan revisions to identify changes

### Overlay Comparison
```
browser → snapshot → upload revised plan set
browser → snapshot → select original and revised sheets
browser → snapshot → use "Compare" or "Overlay" tool
browser → snapshot → review highlighted differences
browser → snapshot → note areas requiring re-measurement
```

### Re-Takeoff Workflow
1. Upload revised plans
2. Compare with original (overlay)
3. Re-measure changed areas only
4. Update estimate quantities
5. Create change order if scope increased

---

## Step 9: Takeoff → Estimate → Proposal Pipeline

### Complete Flow
```
1. Upload Plans    → /app/Plans
2. Calibrate Scale → Set known dimension
3. Measure         → Linear, Area, Count tools
4. Assign to Estimate → Link to cost codes/line items
5. Complete Estimate   → Set unit costs, markup
6. Create Proposal     → Format for client
7. Send to Budget      → Activate Job Costing Budget
```

### Estimate View Toggle
The Estimate supports a "Takeoff Assemblies" view:
```
browser → navigate to https://buildertrend.net/app/Estimate
browser → snapshot → click "Switch Views"
browser → snapshot → select "Takeoff Assemblies"
browser → snapshot → view measurements organized by assembly
```

**Available Estimate Views:**
- Cost Code view
- Groups view
- List view
- Takeoff Assemblies view

---

## Batch Mode: Multi-Sheet Takeoff
For large plan sets with multiple sheets:

1. Upload all sheets at once
2. Calibrate each sheet individually (scales may differ)
3. Work through sheets systematically: Architectural → Structural → MEP
4. Use consistent layer naming across sheets
5. Review running totals per layer/cost code
6. Export all measurements to estimate in one batch

**Message to the user (Takeoff Summary):**
```
📐 Takeoff Complete for [Project]:
| Trade | Measurement | Quantity | Unit | Cost Code |
|---|---|---|---|---|
| Framing | Wall lengths | 450 | LF | 05.00 |
| Flooring | Floor area | 2,100 | SF | 15.00 |
| Painting | Wall/ceiling | 4,800 | SF | 14.00 |
| Electrical | Outlets | 42 | EA | 08.00 |
| Plumbing | Fixtures | 8 | EA | 07.00 |

Ready to send to Estimate?
```

**Inline buttons:**
| Button | Style | callback_data |
|---|---|---|
| ✅ Send to Estimate | `success` | `takeoff_to_estimate` |
| ✏️ Review Measurements | `primary` | `takeoff_review` |
| 📐 Re-measure a Sheet | `primary` | `takeoff_remeasure` |
| ❌ Cancel | `danger` | `takeoff_cancel` |

---

## Error Handling

| Error | Action |
|---|---|
| BT session expired | Stop, notify the user to re-login |
| Plan upload failed | Check file format (PDF required), check file size |
| Calibration inaccurate | Re-calibrate using a longer known dimension |
| Measurements not linking to estimate | Verify launched from Estimate, check cost code assignment |
| Plan resolution too low | Request higher-resolution PDF from architect |
| Scale varies between sheets | Calibrate each sheet individually |
| Overlay comparison misaligned | Ensure both plans are same scale/orientation |

---

## Learning Academy Reference
- **Course:** "Buildertrend Takeoff" — 10 activities, 30 min
- **Course:** "Takeoff Live Training: On-Demand" — live demo
- **Key Topics:** Scale calibration, measurement tools, estimate integration

---

## Company-Specific Notes
- **Takeoff Settings:** `/app/Settings/TakeoffSettings`
- Plans stored per job in `/app/Plans`
- Specifications (text-based) in Plans → Specs tab
- Takeoff quantities feed directly into estimates and procurement agent's requests
- For external takeoffs (Square Takeoff), import via Estimate → External Import
