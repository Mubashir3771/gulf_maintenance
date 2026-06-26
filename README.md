# Gulf Maintenance

A custom Frappe/ERPNext **v16** app that takes a maintenance job from intake all the way to a
**billable Sales Invoice**. Field technicians log parts and labour against customer equipment; an
approval gate protects against expensive part consumption; the office signs off and generates a
draft invoice that posts inventory, COGS and revenue from a single document.

Tested on site `gulfdesk.com` (frappe 16.16, erpnext 16.15). End-to-end smoke test:
**24/24 checks passing** across the under-threshold and over-threshold paths, with GL entries
verified on a submitted invoice.

The flow:

```
Draft → Assigned → Awaiting Approval → In Progress → Completed → Signed Off → Billed
```

This README is organised to mirror the five deliverables: (1) DocType structure, (2) Workflow &
permissions, (3) the approval gate, (4) billing logic & GL, (5) written walkthrough + design
choices + how AI was used.

---

## 1. DocType structure

Module: **Gulf Maintenance**. Three custom DocTypes plus three roles. DocTypes are written to disk
as JSON (developer mode) and version-controlled.

### 1.1 Equipment

A customer-owned physical unit being serviced — deliberately **not** a stock Item (see design
choices). Naming: `EQP-.#####`.

| Fieldname | Type | Links to | Notes |
|---|---|---|---|
| `customer` | Link | **Customer** | Mandatory, in list view — who owns the unit |
| `equipment_name` | Data | — | Mandatory |
| `model` | Data | — | |
| `serial_no` | Data | — | Mandatory; identifies the individual unit |
| `install_date` | Date | — | |
| `warranty_expiry` | Date | — | |
| `location` | Small Text | — | Where the unit physically sits |

Service history is surfaced through the doctype's **dashboard Links** (related Maintenance
Requests), so a separate history child table is not needed.

### 1.2 Parts Used  *(child table, `istable = 1`)*

| Fieldname | Type | Links to | Notes |
|---|---|---|---|
| `item` | Link | **Item** | Mandatory — a real stock item |
| `item_name` | Data | — | Read-only, fetched from `item.item_name` |
| `warehouse` | Link | **Warehouse** | Stock location the part is consumed from |
| `qty` | Float | — | Default 1, mandatory |
| `rate` | Currency | — | Defaults from the Item, editable |
| `amount` | Currency | — | Read-only, computed `qty × rate` |

### 1.3 Maintenance Request  *(parent — not submittable; state driven by the Workflow)*

| Fieldname | Type | Links to | Notes |
|---|---|---|---|
| `naming_series` | Select | — | `MREQ-.YYYY.-` |
| `customer` | Link | **Customer** | Mandatory |
| `equipment` | Link | **Equipment** | Link query filtered to the chosen `customer` |
| `issue_description` | Small Text | — | Mandatory |
| `priority` | Select | — | Low / Medium / High / Urgent (default Medium) |
| `technician` | Link | **Employee** | Assigned technician |
| `parts_used` | Table | **Parts Used** | Child table of consumed parts |
| `total_parts_cost` | Currency | — | Read-only; summed **server-side** in `validate()` |
| `parts_approved` | Check | — | Read-only; set only by the *Approve Parts* transition |
| `hours_spent` | Float | — | Labour hours |
| `labour_rate` | Currency | — | Rate used for the labour invoice line |
| `work_done` | Text | — | Technician's completion notes |
| `customer_signoff` | Check | — | Read-only; set by *Customer Sign-off* |
| `signoff_date` | Date | — | Read-only; stamped at sign-off |
| `sales_invoice` | Link | **Sales Invoice** | Read-only; set when billed |
| `workflow_state` | Link | **Workflow State** | Read-only; managed by the Workflow |

**Why this structure.** The parent holds the whole job lifecycle; parts are a child table because a
request has many parts and each needs its own item/warehouse/qty/rate. Links point at standard
ERPNext masters (Customer, Item, Warehouse, Employee, Sales Invoice) so the app plugs into native
stock, HR and accounting instead of duplicating them. Totals live on the parent and are recomputed
server-side so they're reliable even on API/import writes.

---

## 2. Workflow, roles & permissions

Three roles: **Maintenance User** (intake/office/billing), **Maintenance Technician**,
**Maintenance Manager**.

### 2.1 States & transitions (Workflow: "Maintenance Request")

| Action | From → To | Allowed role | Condition / effect |
|---|---|---|---|
| Assign | Draft → Assigned | Maintenance User | requires `technician` |
| Submit for Approval | Assigned → Awaiting Approval | Technician / User | used when parts > 10,000 |
| Start Work | Assigned → In Progress | Maintenance Technician | only when `total_parts_cost ≤ 10000` |
| Approve Parts | Awaiting Approval → In Progress | Maintenance Manager | sets `parts_approved = 1` |
| Reject | Awaiting Approval → Assigned | Maintenance Manager | sends back |
| Mark Complete | In Progress → Completed | Maintenance Technician | work_done / hours |
| Customer Sign-off | Completed → Signed Off | Maintenance User | sets `customer_signoff`, `signoff_date` |
| Create Invoice / Mark Billed | Signed Off → Billed | Maintenance User | via the billing button |

Native Frappe features used: **Assignment** (a ToDo can be assigned to the technician on *Assign*),
**Notification** (the `Maintenance Manager` is alerted when a request enters *Awaiting Approval*),
and **Workflow** itself for the state machine and transition permissions.

### 2.2 Permissions on this app's DocTypes  *(in the JSON, version-controlled)*

| | Maintenance User | Maintenance Technician | Maintenance Manager | System Manager |
|---|---|---|---|---|
| **Equipment** | read/write/create | read | all | all |
| **Maintenance Request** | read/write/create | read/write | all | all |

### 2.3 Access to the standard DocTypes the forms depend on

A Maintenance Request form is only usable if the user can *select* a Customer, Equipment, a
technician (Employee) and parts (Item + Warehouse), and the office must be able to raise the draft
invoice. These reads are granted to the maintenance roles by
`gulf_maintenance.install.setup_role_permissions` (run from `after_install`):

| Standard DocType | Granted to | Access |
|---|---|---|
| Customer, Item, Warehouse, Employee | all three roles | read (select) |
| Sales Invoice | Maintenance User | read/write/create (draft only) |
| Sales Invoice | Maintenance Manager | read |

This is done **in code, not as a `Custom DocPerm` fixture, on purpose**: as soon as a doctype has
*any* Custom DocPerm, Frappe ignores its standard perms — so shipping a few custom rows for a
standard doctype like Customer would silently strip access from Sales/Accounts users. The
`after_install` approach is additive and safe (it preserves existing perms, then adds the
maintenance-role reads). Posting/submitting invoices (the GL step) stays an Accounts function — the
maintenance side only produces the draft.

### 2.4 Desk access

The app ships a public **Workspace** ("Gulf Maintenance") and registers itself via the
`add_to_apps_screen` hook (logo + route), so it appears in the desk **app switcher**. Note: this
Frappe version (16.16) serves the desk at **`/desk`** and redirects `/app` → `/desk`, so the
workspace opens at **`/desk/gulf-maintenance`**.

Visibility for non-System-Manager users was verified server-side for a user holding **only**
`Maintenance Technician`: the app resolves in `get_apps()`, in the boot `app_data` (app switcher),
and in the workspace sidebar — so the role can reach the workspace and open the doctypes subject to
the permissions above. (The app is treated as "setup not required" since it declares no
`setup_wizard_stages`, which is what lets ordinary roles see it rather than only System Managers.)

---

## 3. The approval gate (the required custom script)

The PKR 10,000 enforcement is a **Server Script** (`Maintenance Parts Approval Gate`, DocType Event
→ *Before Save* on Maintenance Request):

> If `workflow_state` ∈ {In Progress, Completed, Signed Off, Billed} **and**
> `total_parts_cost > 10000` **and** `parts_approved` is not set → `frappe.throw(...)`.

This is the **authoritative** guard — it blocks the save itself, so the rule holds even if the
workflow is edited or a state is set programmatically. The Workflow transition conditions
(`Start Work` only when `≤ 10000`; `Submit for Approval` only when `> 10000`) are a complementary,
UI-level layer.

### Prerequisite — enable server scripts (bench-wide)

Server Scripts run only when enabled, and Frappe by design reads this flag **only from
`common_site_config.json` (bench-wide)**, not per-site:

```bash
bench set-config -g server_script_enabled 1
```

(`bench --site … set-config` writes the *site* config, which Frappe ignores for this flag — see the
AI notes.)

---

## 4. Billing logic & GL

A **Client Script** on Maintenance Request shows a **"Create Sales Invoice"** button when
`workflow_state == "Signed Off"` and `sales_invoice` is empty. It calls the whitelisted method
`gulf_maintenance.api.create_sales_invoice` (`@frappe.whitelist()`), which re-checks the request is
Signed Off, has something to bill and isn't already invoiced, then builds the SI:

- one **stock line per part** (item, qty, rate, **warehouse** from the row);
- one separate **labour line** — the non-stock service Item `Maintenance Labour`
  (`is_stock_item = 0`), `qty = hours_spent`, `rate = labour_rate`;
- `update_stock = 1`, inserted as a **Draft** (never auto-submitted);
- then links the SI back onto the request and moves it to *Billed*.

**GL considerations.** While the invoice is a **Draft**, no GL is posted — giving the office a
review window. **On submit** of an Update-Stock SI, GL posts (verified on a real submitted test
invoice — parts 16,000 + labour 4,000):

| Account | Dr | Cr |
|---|---|---|
| Debtors | 20,000 | |
| Sales | | 20,000 |
| Cost of Goods Sold | 16,000 | |
| Stock In Hand | | 16,000 |

Revenue posts `Dr Debtors / Cr Sales`; because Update Stock is on, the consumed parts also post
`Dr COGS / Cr Stock-in-hand` (valuation) from the same document. The labour line is non-stock →
revenue only, no inventory impact. This requires correct Income / COGS accounts, item groups and a
default warehouse on the Company. The `Maintenance Labour` item is created automatically by
`gulf_maintenance.install.after_install` (create-if-not-exists) so the build is self-contained.

---

## 5. Walkthrough, design choices & how AI was used

### 5.1 Flow walkthrough

1. **Intake** — Office creates a Maintenance Request, picks the Customer and the customer's
   Equipment (link filtered to that customer), describes the issue, assigns a technician.
2. **Parts & approval** — Technician adds Parts Used (stock items + warehouse); `total_parts_cost`
   is summed server-side. ≤ 10k → *Start Work* straight to *In Progress*; > 10k → *Submit for
   Approval* → manager notified → *Approve Parts* (or *Reject*).
3. **Work** — Technician records `work_done` / `hours_spent`, then *Mark Complete*.
4. **Sign-off** — Office does an internal *Customer Sign-off* (stamps the checkbox + date).
5. **Billing** — The *Create Sales Invoice* button builds the draft invoice and marks the request
   *Billed*.

### 5.2 Design choices

- **Equipment is a dedicated DocType, not an Item.** It represents an individual serialised unit a
  customer owns, with its own warranty/install lifecycle and service history — conceptually distinct
  from a catalogue Item you buy/sell, and not something the company carries in stock.
- **Internal sign-off only.** The office marks sign-off on the customer's behalf. For production, a
  **portal sign-off** (Web Form / authenticated portal action) is the recommended approach — a real
  customer audit trail instead of an internal checkbox.
- **Parts billed via an Update-Stock Sales Invoice.** A single document both consumes inventory
  (posting valuation/COGS) and bills the customer — simpler and less error-prone than keeping a
  separate Stock Entry and Sales Invoice in sync, and it guarantees the customer is billed for
  exactly the parts that left stock.
- **Single role + single threshold (PKR 10,000).** The brief defines one threshold, so one
  `Maintenance Manager` role and one limit is right-sized; tiers would be over-engineering. If
  hierarchy were needed later, the threshold could move to a Settings field and tiers added, routing
  via the Employee **"Reports To"** chain. Approval is **role-based** (any Maintenance Manager) rather
  than per-technician routing — appropriate for a small office.
- **Invoice left as a Draft** — deliberately not auto-submitted, so no GL posts before the office
  reviews.
- **Server-side totals** — `total_parts_cost` / row `amount` recomputed in `validate()`, reliable for
  API/import/scripted writes, not just the UI.

### 5.3 How AI was used

This app was built end-to-end by an AI agent (Claude) in the bench: it created the DocTypes,
controller, API, Workflow, scripts and fixtures, then drove a 24-check end-to-end test through
`bench execute` before committing. AI was strong at scaffolding and at verifying field names against
the *actually installed* v16 rather than assuming them. It also got things wrong and had to debug:

1. **`server_script_enabled` — site vs bench config (headline bug).** The gate first refused to run
   with `ServerScriptNotEnabled` even though `bench --site … set-config server_script_enabled 1` had
   "succeeded". Reading `frappe/utils/safe_exec.py` showed the flag is read from
   `get_common_site_config()` — *"server scripts can only be enabled via common_site_config.json"*.
   Fix: the bench-wide form `bench set-config -g server_script_enabled 1`.
2. **Workflow wouldn't insert.** Creating the Workflow raised `LinkValidationError` because the
   `Workflow State` / `Workflow Action Master` masters didn't exist yet — this version validates
   those links before auto-creation. Fixed by creating the masters first.
3. **The site wasn't actually set up.** The first labour-Item creation failed — no Item Groups, UOMs,
   Company or warehouses (the ERPNext setup wizard had never been completed). The wizard was run
   programmatically (Pakistan / PKR, "Gulf Maintenance LLC") to get a chart of accounts, default
   Income/COGS/Stock accounts and a default warehouse, which the Update-Stock invoice needs.

Each was diagnosed by reading the actual traceback/source rather than guessing.

---

## Version control / fixtures

DB-stored configuration is exported to git via `fixtures` in `hooks.py`, each filtered to only this
app's records: the 3 **Roles**, the **Workflow** (+ **Workflow State** and **Workflow Action
Master**), the **Server Script**, the **Client Script**, the **Notification**, and the **Workspace**.
DocTypes themselves are JSON on disk (developer mode).

> **Fresh-install ordering.** Fixtures import in alphabetical filename order, so `workflow.json`
> imports *before* `workflow_action_master.json` / `workflow_state.json` — and the Workflow links to
> those masters. To avoid a `LinkValidationError` on a clean install, `after_install` (which runs
> *before* fixtures sync) pre-creates the roles and the Workflow State / Action Master records; the
> fixtures then re-import them with full definitions.

```bash
bench --site <site> migrate
bench --site <site> export-fixtures
```

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app <repo-url> --branch main
bench --site <site> install-app gulf_maintenance
bench set-config -g server_script_enabled 1   # required for the approval gate
bench --site <site> migrate
```

## License

mit