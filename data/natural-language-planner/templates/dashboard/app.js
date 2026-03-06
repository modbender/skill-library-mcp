/**
 * NL Planner — Dashboard Application
 *
 * Single-page app that reads task/project data from the local Python API
 * and presents it as a weekly focus view, Kanban board, project overview,
 * and timeline.  Supports dark mode and image galleries in task details.
 */

(function () {
  "use strict";

  // ── Configuration ───────────────────────────────────────────────
  const API_BASE = window.location.origin;
  const POLL_INTERVAL_MS = 5000;
  const IMG_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp"];

  // ── State ───────────────────────────────────────────────────────
  let allTasks = [];
  let archivedTasks = [];
  let allProjects = [];
  let stats = {};
  let taskDetails = {};        // Cache of full task bodies keyed by id
  let currentView = "focus";   // Default to This Week view
  let pollTimer = null;

  // Maps: project-id → hex colour, project-id → [tags]
  let projectColorMap = {};
  let projectTagsMap = {};

  // ── DOM helpers ─────────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const els = {
    body: document.body,
    searchInput: $("#search-input"),
    btnRefresh: $("#btn-refresh"),
    btnTheme: $("#btn-theme"),
    tabs: $$(".tab"),
    views: $$(".view"),
    // Stats
    statTotal: $("#stat-total"),
    statTodo: $("#stat-todo"),
    statProgress: $("#stat-progress"),
    statDone: $("#stat-done"),
    statOverdue: $("#stat-overdue"),
    statProjects: $("#stat-projects"),
    // This Week
    weekDateRange: $("#week-date-range"),
    weekGrid: $("#week-grid"),
    // Kanban columns
    colTodo: $("#col-todo"),
    colProgress: $("#col-progress"),
    colDone: $("#col-done"),
    colCountTodo: $("#col-count-todo"),
    colCountProgress: $("#col-count-progress"),
    colCountDone: $("#col-count-done"),
    // Projects
    projectsGrid: $("#projects-grid"),
    // Timeline
    timeline: $("#timeline"),
    // Archive
    archiveList: $("#archive-list"),
    archiveCount: $("#archive-count"),
    // Search
    viewSearch: $("#view-search"),
    searchResults: $("#search-results"),
    // Modal
    modalOverlay: $("#modal-overlay"),
    modalTitle: $("#modal-title"),
    modalStatus: $("#modal-status"),
    modalPriority: $("#modal-priority"),
    modalProject: $("#modal-project"),
    modalDue: $("#modal-due"),
    modalCreated: $("#modal-created"),
    modalTags: $("#modal-tags"),
    modalBody: $("#modal-body"),
    modalContext: $("#modal-context"),
    modalContextText: $("#modal-context-text"),
    modalDeps: $("#modal-deps"),
    modalGallery: $("#modal-gallery"),
    galleryGrid: $("#gallery-grid"),
    modalClose: $("#modal-close"),
    // Agent Tips
    modalAgentTips: $("#modal-agent-tips"),
    agentTipsHeader: $("#agent-tips-header"),
    agentTipsChevron: $("#agent-tips-chevron"),
    agentTipsBody: $("#agent-tips-body"),
    agentTipsList: $("#agent-tips-list"),
    // Lightbox
    lightboxOverlay: $("#lightbox-overlay"),
    lightboxImg: $("#lightbox-img"),
  };

  // ── Theme ───────────────────────────────────────────────────────

  function initTheme() {
    const saved = localStorage.getItem("nlp-theme");
    if (saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      els.body.classList.add("dark");
    }
  }

  function toggleTheme() {
    els.body.classList.toggle("dark");
    localStorage.setItem("nlp-theme", els.body.classList.contains("dark") ? "dark" : "light");
  }

  // ── API helpers ─────────────────────────────────────────────────

  async function api(endpoint) {
    try {
      const resp = await fetch(`${API_BASE}${endpoint}`);
      if (!resp.ok) return null;
      return await resp.json();
    } catch (err) {
      console.warn(`API call failed: ${endpoint}`, err);
      return null;
    }
  }

  // ── Data loading ────────────────────────────────────────────────

  async function loadAll() {
    const [s, p, t, a] = await Promise.all([
      api("/api/stats"),
      api("/api/projects"),
      api("/api/tasks"),
      api("/api/tasks?include_archived=true"),
    ]);
    if (s) stats = s;
    if (p) allProjects = p;
    if (t) allTasks = t;
    // Archived tasks = everything from the include_archived call that has status "archived"
    if (a) archivedTasks = a.filter((task) => task.status === "archived");
    buildProjectMaps();
    render();
  }

  /**
   * Build lookup maps from project data so that tags and cards
   * throughout the dashboard can be colour-coded to match their
   * parent project.
   */
  function buildProjectMaps() {
    projectColorMap = {};
    projectTagsMap = {};
    for (const p of allProjects) {
      const pid = p.id || p.title;
      if (p.color) projectColorMap[pid] = p.color;
      if (p.tags) projectTagsMap[pid] = p.tags;
    }
  }

  /**
   * Return the project colour for a given project ID, or "" if none.
   */
  function getProjectColor(projectId) {
    return projectColorMap[projectId] || "";
  }

  /**
   * Given a tag name, find the colour of the project that owns it.
   * If multiple projects share the same tag, the first match wins.
   */
  function getTagColor(tag) {
    for (const p of allProjects) {
      const pid = p.id || p.title;
      if ((p.tags || []).includes(tag) && p.color) return p.color;
    }
    return "";
  }

  /**
   * Render a tag span, optionally coloured to its owning project.
   */
  function tagHTML(tagName, projectId) {
    // Try project-specific colour first, then fall back to tag lookup
    const color = (projectId && getProjectColor(projectId)) || getTagColor(tagName);
    if (color) {
      return `<span class="tag" style="color:${esc(color)};background:${esc(color)}18">${esc(tagName)}</span>`;
    }
    return `<span class="tag">${esc(tagName)}</span>`;
  }

  async function loadTaskDetail(taskId) {
    // Always fetch fresh detail — don't serve stale cache
    const detail = await api(`/api/task/${encodeURIComponent(taskId)}`);
    if (detail) taskDetails[taskId] = detail;
    return detail || taskDetails[taskId] || null;
  }

  // ── Rendering ───────────────────────────────────────────────────

  function render() {
    renderStats();
    renderWeekFocus();
    renderBoard();
    renderProjects();
    renderTimeline();
    renderArchive();
  }

  function renderStats() {
    els.statTotal.textContent = stats.total_tasks ?? "—";
    els.statTodo.textContent = stats.by_status?.todo ?? "—";
    els.statProgress.textContent = stats.by_status?.["in-progress"] ?? "—";
    els.statDone.textContent = stats.by_status?.done ?? "—";
    els.statOverdue.textContent = stats.overdue ?? "—";
    els.statProjects.textContent = stats.active_projects ?? "—";
  }

  // ── This Week Focus ─────────────────────────────────────────────

  function getWeekBounds() {
    const now = new Date();
    const day = now.getDay();
    const mondayOffset = day === 0 ? -6 : 1 - day;
    const monday = new Date(now);
    monday.setDate(now.getDate() + mondayOffset);
    monday.setHours(0, 0, 0, 0);
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    sunday.setHours(23, 59, 59, 999);
    return { monday, sunday };
  }

  function renderWeekFocus() {
    const { monday, sunday } = getWeekBounds();

    // Show date range in header
    els.weekDateRange.textContent =
      `${formatDateShort(monday)} — ${formatDateShort(sunday)}`;

    // A task belongs to "this week" if:
    //  - It's in-progress, OR
    //  - It has a due date this week (and not done/archived), OR
    //  - It's high priority + todo
    const weekTasks = allTasks.filter((t) => {
      if (t.status === "done" || t.status === "archived") return false;
      if (t.status === "in-progress") return true;
      if (t.due) {
        const dueDate = new Date(t.due + "T23:59:59");
        if (dueDate >= monday && dueDate <= sunday) return true;
        // Also include overdue
        if (dueDate < monday) return true;
      }
      if (t.priority === "high" && t.status === "todo") return true;
      return false;
    });

    // Sort: overdue first, then in-progress, then by priority, then by due date
    weekTasks.sort((a, b) => {
      const aOverdue = a.due && new Date(a.due + "T23:59:59") < new Date() ? 0 : 1;
      const bOverdue = b.due && new Date(b.due + "T23:59:59") < new Date() ? 0 : 1;
      if (aOverdue !== bOverdue) return aOverdue - bOverdue;

      const statusOrder = { "in-progress": 0, "todo": 1 };
      const aS = statusOrder[a.status] ?? 2;
      const bS = statusOrder[b.status] ?? 2;
      if (aS !== bS) return aS - bS;

      const prioOrder = { "high": 0, "medium": 1, "low": 2 };
      const aP = prioOrder[a.priority] ?? 1;
      const bP = prioOrder[b.priority] ?? 1;
      if (aP !== bP) return aP - bP;

      return (a.due || "9999") > (b.due || "9999") ? 1 : -1;
    });

    if (!weekTasks.length) {
      els.weekGrid.innerHTML =
        '<div class="week-empty">No tasks this week. Tell your assistant what you\'re working on!</div>';
      return;
    }

    els.weekGrid.innerHTML = weekTasks.map(focusCardHTML).join("");

    // Attach click handlers
    els.weekGrid.querySelectorAll(".focus-card").forEach((card) => {
      card.addEventListener("click", () => openModal(card.dataset.id));
    });
  }

  function focusCardHTML(task) {
    const isOverdue = task.due && new Date(task.due + "T23:59:59") < new Date();
    const dueLabel = task.due ? formatDate(task.due) : "";
    const dueClass = isOverdue ? "overdue" : "";
    const tags = (task.tags || [])
      .slice(0, 4)
      .map((t) => tagHTML(t, task.project))
      .join("");
    const desc = task.description || "";
    const deps = task.dependencies || [];
    const banner = buildBannerUrl(task);
    const pColor = getProjectColor(task.project);
    const borderStyle = pColor ? `style="border-left:3px solid ${esc(pColor)}"` : "";

    return `
      <div class="focus-card ${banner ? "has-banner" : ""}" data-id="${esc(task.id)}" ${borderStyle}>
        ${banner ? `<div class="card-banner card-banner-lg"><img src="${esc(banner)}" alt="" loading="lazy" /></div>` : ""}
        <div class="focus-card-content">
          <div class="focus-card-top">
            <div class="focus-card-title">
              <span class="priority-dot priority-${task.priority || "medium"}"></span>
              ${esc(task.title)}
            </div>
            <div class="focus-card-badges">
              <span class="badge badge-sm badge-${task.status || "todo"}">${esc(task.status || "todo")}</span>
            </div>
          </div>
          ${desc ? `<div class="focus-card-desc">${esc(desc)}</div>` : ""}
          <div class="focus-card-footer">
            ${task.project ? `<span class="focus-card-project">${esc(task.project)}</span>` : ""}
            ${dueLabel ? `<span class="focus-card-due ${dueClass}">${isOverdue ? "Overdue: " : "Due "}${dueLabel}</span>` : ""}
            ${tags}
          </div>
          ${deps.length ? `<div class="focus-card-deps"><strong>Depends on:</strong> ${deps.map(esc).join(", ")}</div>` : ""}
        </div>
      </div>`;
  }

  // ── Board ───────────────────────────────────────────────────────

  function renderBoard() {
    const buckets = { todo: [], "in-progress": [], done: [] };
    for (const task of allTasks) {
      const s = task.status || "todo";
      if (buckets[s]) buckets[s].push(task);
    }

    els.colTodo.innerHTML = buckets.todo.map(taskCardHTML).join("");
    els.colProgress.innerHTML = buckets["in-progress"].map(taskCardHTML).join("");
    els.colDone.innerHTML = buckets.done.map(taskCardHTML).join("");

    els.colCountTodo.textContent = buckets.todo.length;
    els.colCountProgress.textContent = buckets["in-progress"].length;
    els.colCountDone.textContent = buckets.done.length;

    attachCardClicks();
  }

  function taskCardHTML(task) {
    const dueClass = task.due && new Date(task.due) < new Date() ? "overdue" : "";
    const dueLabel = task.due ? formatDate(task.due) : "";
    const tags = (task.tags || [])
      .slice(0, 3)
      .map((t) => tagHTML(t, task.project))
      .join("");
    const banner = buildBannerUrl(task);
    const pColor = getProjectColor(task.project);
    const borderStyle = pColor ? `style="border-left:3px solid ${esc(pColor)}"` : "";

    return `
      <div class="task-card ${banner ? "has-banner" : ""}" data-id="${esc(task.id)}" ${borderStyle}>
        ${banner ? `<div class="card-banner"><img src="${esc(banner)}" alt="" loading="lazy" /></div>` : ""}
        <div class="task-card-body">
          <div class="task-card-title">
            <span class="priority-dot priority-${task.priority || "medium"}"></span>
            ${esc(task.title)}
          </div>
          <div class="task-card-meta">
            <span class="task-card-project">${esc(task.project || "")}</span>
            ${dueLabel ? `<span class="task-card-due ${dueClass}">${dueLabel}</span>` : ""}
            ${tags}
          </div>
        </div>
      </div>`;
  }

  function attachCardClicks() {
    $$(".task-card").forEach((card) => {
      card.addEventListener("click", () => openModal(card.dataset.id));
    });
  }

  // ── Projects ────────────────────────────────────────────────────

  function renderProjects() {
    if (!allProjects.length) {
      els.projectsGrid.innerHTML =
        '<p class="timeline-empty">No projects yet.</p>';
      return;
    }

    els.projectsGrid.innerHTML = allProjects
      .map((p) => {
        const pid = p.id || p.title;
        const tasks = allTasks.filter((t) => t.project === pid);
        const todoCount = tasks.filter((t) => t.status === "todo").length;
        const progressCount = tasks.filter((t) => t.status === "in-progress").length;
        const doneCount = tasks.filter((t) => t.status === "done").length;
        const pColor = p.color || "";
        const tags = (p.tags || [])
          .map((t) => {
            if (pColor) {
              return `<span class="tag" style="color:${esc(pColor)};background:${esc(pColor)}18">${esc(t)}</span>`;
            }
            return `<span class="tag">${esc(t)}</span>`;
          })
          .join("");
        const borderStyle = pColor ? `style="border-left:3px solid ${esc(pColor)}"` : "";

        return `
          <div class="project-card" ${borderStyle}>
            <div class="project-card-title">${esc(p.title || pid)}</div>
            <div class="project-card-status">${esc(p.status || "active")}</div>
            <div class="project-card-counts">
              <span><strong>${todoCount}</strong> todo</span>
              <span><strong>${progressCount}</strong> in progress</span>
              <span><strong>${doneCount}</strong> done</span>
            </div>
            ${tags ? `<div class="project-card-tags">${tags}</div>` : ""}
          </div>`;
      })
      .join("");
  }

  // ── Timeline ────────────────────────────────────────────────────

  function renderTimeline() {
    const withDue = allTasks
      .filter((t) => t.due && t.status !== "done" && t.status !== "archived")
      .sort((a, b) => (a.due > b.due ? 1 : -1));

    if (!withDue.length) {
      els.timeline.innerHTML =
        '<p class="timeline-empty">No upcoming deadlines.</p>';
      return;
    }

    const groups = {};
    for (const task of withDue) {
      const d = task.due;
      if (!groups[d]) groups[d] = [];
      groups[d].push(task);
    }

    els.timeline.innerHTML = Object.entries(groups)
      .map(
        ([dateStr, tasks]) => `
        <div class="timeline-group">
          <div class="timeline-date">${formatDate(dateStr)}${isOverdue(dateStr) ? ' <span style="color:var(--red)">(overdue)</span>' : ""}</div>
          ${tasks
            .map(
              (t) => {
                const tc = getProjectColor(t.project);
                const dotAttr = tc
                  ? `class="priority-dot" style="background:${esc(tc)}"`
                  : `class="priority-dot priority-${t.priority || "medium"}"`;
                return `
            <div class="timeline-item" data-id="${esc(t.id)}">
              <span ${dotAttr}></span>
              <span class="timeline-item-title">${esc(t.title)}</span>
              <span class="timeline-item-project">${esc(t.project || "")}</span>
            </div>`;
              }
            )
            .join("")}
        </div>`
      )
      .join("");

    $$(".timeline-item").forEach((item) => {
      item.addEventListener("click", () => openModal(item.dataset.id));
    });
  }

  // ── Archive ─────────────────────────────────────────────────────

  function renderArchive() {
    if (!archivedTasks.length) {
      els.archiveCount.textContent = "";
      els.archiveList.innerHTML =
        '<p class="archive-empty">No archived tasks yet. Completed tasks will appear here once archived.</p>';
      return;
    }

    els.archiveCount.textContent = `${archivedTasks.length} task${archivedTasks.length === 1 ? "" : "s"}`;

    // Sort by done/updated date descending (most recently archived first),
    // fall back to created date
    const sorted = [...archivedTasks].sort((a, b) => {
      const dateA = a.done_date || a.updated || a.created || "";
      const dateB = b.done_date || b.updated || b.created || "";
      return dateB > dateA ? 1 : dateB < dateA ? -1 : 0;
    });

    // Group by month
    const groups = {};
    for (const task of sorted) {
      const raw = task.done_date || task.updated || task.created || "";
      const key = raw ? formatMonth(raw) : "Unknown";
      if (!groups[key]) groups[key] = [];
      groups[key].push(task);
    }

    els.archiveList.innerHTML = Object.entries(groups)
      .map(
        ([month, tasks]) => `
        <div class="archive-month-group">
          <div class="archive-month-header">
            <span class="archive-month-label">${esc(month)}</span>
            <span class="archive-month-count">${tasks.length}</span>
          </div>
          <div class="archive-month-items">
            ${tasks.map(archiveItemHTML).join("")}
          </div>
        </div>`
      )
      .join("");

    // Attach click handlers
    els.archiveList.querySelectorAll(".archive-item").forEach((item) => {
      item.addEventListener("click", () => openModal(item.dataset.id));
    });
  }

  function archiveItemHTML(task) {
    const tags = (task.tags || [])
      .slice(0, 4)
      .map((t) => tagHTML(t, task.project))
      .join("");
    const doneDate = task.done_date || task.updated || "";
    const pColor = getProjectColor(task.project);
    const borderStyle = pColor ? `style="border-left:3px solid ${esc(pColor)}"` : "";

    return `
      <div class="archive-item" data-id="${esc(task.id)}" ${borderStyle}>
        <div class="archive-item-title">${esc(task.title)}</div>
        <div class="archive-item-meta">
          ${task.project ? `<span class="archive-item-project">${esc(task.project)}</span>` : ""}
          ${doneDate ? `<span class="archive-item-date">${formatDate(doneDate)}</span>` : ""}
          ${tags}
        </div>
      </div>`;
  }

  function formatMonth(iso) {
    if (!iso) return "Unknown";
    try {
      const d = new Date(iso + (iso.includes("T") ? "" : "T00:00:00"));
      return d.toLocaleDateString(undefined, { month: "long", year: "numeric" });
    } catch {
      return "Unknown";
    }
  }

  // ── Search ──────────────────────────────────────────────────────

  let searchDebounce = null;

  function handleSearch() {
    const query = els.searchInput.value.trim();
    if (!query) {
      hideSearch();
      return;
    }
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(async () => {
      const results = await api(`/api/search?q=${encodeURIComponent(query)}`);
      showSearch(results || []);
    }, 300);
  }

  function showSearch(results) {
    els.views.forEach((v) => v.classList.remove("active"));
    els.viewSearch.style.display = "block";
    els.viewSearch.classList.add("active");

    if (!results.length) {
      els.searchResults.innerHTML =
        '<p class="search-empty">No tasks found.</p>';
      return;
    }

    els.searchResults.innerHTML = results.map(taskCardHTML).join("");
    attachCardClicks();
  }

  function hideSearch() {
    els.viewSearch.style.display = "none";
    els.viewSearch.classList.remove("active");
    switchView(currentView);
  }

  // ── Modal (with full detail, context, and gallery) ──────────────

  async function openModal(taskId) {
    // Start with list data for instant display (check active tasks, then archive)
    const listTask = allTasks.find((t) => t.id === taskId)
      || archivedTasks.find((t) => t.id === taskId);
    if (!listTask) return;
    populateModal(listTask, null);
    els.modalOverlay.classList.add("open");

    // Then fetch full detail (body, context, attachments)
    const detail = await loadTaskDetail(taskId);
    if (detail) {
      populateModal(listTask, detail);
    }
  }

  function populateModal(task, detail) {
    const statusClass = `badge-${task.status || "todo"}`;
    const priorityClass = `badge-priority-${task.priority || "medium"}`;

    els.modalStatus.className = `badge ${statusClass}`;
    els.modalStatus.textContent = task.status || "todo";
    els.modalPriority.className = `badge badge-priority ${priorityClass}`;
    els.modalPriority.textContent = task.priority || "medium";

    els.modalTitle.textContent = task.title || "";
    els.modalProject.textContent = task.project ? `Project: ${task.project}` : "";
    els.modalDue.textContent = task.due ? `Due: ${formatDate(task.due)}` : "";
    els.modalCreated.textContent = task.created ? `Created: ${formatDate(task.created)}` : "";

    els.modalTags.innerHTML = (task.tags || [])
      .map((t) => tagHTML(t, task.project))
      .join("");

    // Body — extract description and other sections from full detail
    if (detail && detail.body) {
      const sections = parseBodySections(detail.body);
      els.modalBody.textContent = sections.description || task.description || "";

      // Context section
      if (sections.context) {
        els.modalContext.style.display = "block";
        els.modalContextText.textContent = sections.context;
      } else {
        els.modalContext.style.display = "none";
      }

      // Notes — append to body
      if (sections.notes) {
        els.modalBody.textContent += "\n\n" + sections.notes;
      }
    } else {
      els.modalBody.textContent = task.description || "";
      els.modalContext.style.display = "none";
    }

    // Dependencies
    const deps = task.dependencies || [];
    if (deps.length) {
      els.modalDeps.innerHTML = `<strong>Dependencies:</strong> ${deps.map(esc).join(", ")}`;
    } else {
      els.modalDeps.innerHTML = "";
    }

    // Attachments gallery
    renderGallery(task, detail);

    // Agent Tips panel
    renderAgentTips(detail);
  }

  function renderGallery(task, detail) {
    // Collect attachment paths from the body
    const attachments = [];
    const projectId = task.project || "inbox";

    if (detail && detail.body) {
      // Parse markdown links: [name](path)
      const linkRegex = /\[([^\]]*)\]\(([^)]+)\)/g;
      let match;
      while ((match = linkRegex.exec(detail.body)) !== null) {
        const name = match[1];
        const path = match[2];
        const ext = path.split(".").pop().toLowerCase();
        if (IMG_EXTENSIONS.includes(ext)) {
          attachments.push({ name: name || path.split("/").pop(), path, ext });
        }
      }
    }

    // Also check for attachment files via the API
    if (detail && detail.meta && detail.meta.project) {
      // Build URL for attachment serving
      const baseUrl = `${API_BASE}/api/attachment/${encodeURIComponent(detail.meta.project)}`;
      // We'll also parse the Attachments section
      if (detail.body) {
        const attSection = detail.body.split("## Attachments")[1];
        if (attSection) {
          const fileRegex = /\[([^\]]*)\]\(([^)]+)\)/g;
          let m;
          while ((m = fileRegex.exec(attSection)) !== null) {
            const name = m[1] || m[2].split("/").pop();
            const filePath = m[2];
            const ext = filePath.split(".").pop().toLowerCase();
            const fileName = filePath.split("/").pop();
            if (IMG_EXTENSIONS.includes(ext)) {
              // Avoid duplicates
              if (!attachments.find((a) => a.name === name)) {
                attachments.push({
                  name,
                  path: `${baseUrl}/${encodeURIComponent(fileName)}`,
                  ext,
                  isApiUrl: true,
                });
              }
            }
          }
        }
      }
    }

    if (attachments.length === 0) {
      els.modalGallery.style.display = "none";
      return;
    }

    els.modalGallery.style.display = "block";
    els.galleryGrid.innerHTML = attachments
      .map((att) => {
        const src = att.isApiUrl ? att.path : `${API_BASE}/api/attachment/${encodeURIComponent(projectId)}/${encodeURIComponent(att.path.split("/").pop())}`;
        return `
          <div class="gallery-thumb" data-src="${esc(src)}">
            <img src="${esc(src)}" alt="${esc(att.name)}" loading="lazy" />
            <span class="gallery-thumb-name">${esc(att.name)}</span>
          </div>`;
      })
      .join("");

    // Lightbox handlers
    els.galleryGrid.querySelectorAll(".gallery-thumb").forEach((thumb) => {
      thumb.addEventListener("click", (e) => {
        e.stopPropagation();
        openLightbox(thumb.dataset.src);
      });
    });
  }

  function parseBodySections(body) {
    const sections = { description: "", context: "", notes: "", attachments: "", agentTips: [] };
    const parts = body.split(/^## /m);

    for (const part of parts) {
      const lower = part.toLowerCase();
      if (lower.startsWith("description")) {
        sections.description = part.replace(/^description\s*/i, "").trim();
      } else if (lower.startsWith("context")) {
        sections.context = part.replace(/^context\s*/i, "").trim();
      } else if (lower.startsWith("notes")) {
        sections.notes = part.replace(/^notes\s*/i, "").trim();
      } else if (lower.startsWith("attachments")) {
        sections.attachments = part.replace(/^attachments\s*/i, "").trim();
      } else if (lower.startsWith("agent tips")) {
        const tipsText = part.replace(/^agent tips\s*/i, "").trim();
        sections.agentTips = tipsText
          .split("\n")
          .map((l) => l.trim())
          .filter((l) => l.startsWith("- "))
          .map((l) => l.slice(2));
      } else if (part.trim()) {
        // First section before any heading is also description
        if (!sections.description) sections.description = part.trim();
      }
    }
    return sections;
  }

  function closeModal() {
    els.modalOverlay.classList.remove("open");
  }

  // ── Agent Tips ──────────────────────────────────────────────────

  function renderAgentTips(detail) {
    if (!detail || !detail.body) {
      els.modalAgentTips.style.display = "none";
      return;
    }

    const sections = parseBodySections(detail.body);
    const tips = sections.agentTips || [];

    if (tips.length === 0) {
      els.modalAgentTips.style.display = "none";
      return;
    }

    els.modalAgentTips.style.display = "block";

    const bulbSvg = '<svg class="agent-tip-bullet" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.07" y2="4.93"/></svg>';

    els.agentTipsList.innerHTML = tips
      .map(
        (tip) =>
          `<li class="agent-tip-item">${bulbSvg}<span>${esc(stripMarkdown(tip))}</span></li>`
      )
      .join("");

    // Default to expanded
    els.agentTipsBody.classList.add("open");
    els.agentTipsChevron.classList.add("open");
  }

  function toggleAgentTips() {
    els.agentTipsBody.classList.toggle("open");
    els.agentTipsChevron.classList.toggle("open");
  }

  // ── Lightbox ────────────────────────────────────────────────────

  function openLightbox(src) {
    els.lightboxImg.src = src;
    els.lightboxOverlay.classList.add("open");
  }

  function closeLightbox() {
    els.lightboxOverlay.classList.remove("open");
    els.lightboxImg.src = "";
  }

  // ── View switching ──────────────────────────────────────────────

  function switchView(name) {
    currentView = name;
    els.tabs.forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.view === name);
    });
    els.views.forEach((v) => {
      const match = v.id === `view-${name}`;
      v.classList.toggle("active", match);
      if (v.id === "view-search") v.style.display = match ? "block" : "none";
    });
  }

  // ── Utilities ───────────────────────────────────────────────────

  function buildBannerUrl(task) {
    if (!task.thumbnail) return "";
    const project = task.project || "inbox";
    return `${API_BASE}/api/attachment/${encodeURIComponent(project)}/${encodeURIComponent(task.thumbnail)}`;
  }

  function esc(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
  }

  /** Strip common inline markdown so tips render as clean plain text. */
  function stripMarkdown(str) {
    if (!str) return str;
    return str
      .replace(/\*\*(.+?)\*\*/g, "$1")   // **bold**
      .replace(/__(.+?)__/g, "$1")        // __bold__
      .replace(/\*(.+?)\*/g, "$1")        // *italic*
      .replace(/_(.+?)_/g, "$1")          // _italic_
      .replace(/`(.+?)`/g, "$1")          // `code`
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1 ($2)") // [text](url)
      .replace(/^#+\s+/gm, "")           // headings
      .replace(/~~(.+?)~~/g, "$1");       // ~~strikethrough~~
  }

  function formatDate(iso) {
    if (!iso) return "";
    try {
      const d = new Date(iso + "T00:00:00");
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return iso;
    }
  }

  function formatDateShort(date) {
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }

  function isOverdue(iso) {
    if (!iso) return false;
    try {
      return new Date(iso + "T23:59:59") < new Date();
    } catch {
      return false;
    }
  }

  // ── Event binding ───────────────────────────────────────────────

  function init() {
    // Theme
    initTheme();
    els.btnTheme.addEventListener("click", toggleTheme);

    // Tabs
    els.tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        els.searchInput.value = "";
        hideSearch();
        switchView(tab.dataset.view);
      });
    });

    // Search
    els.searchInput.addEventListener("input", handleSearch);
    els.searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        els.searchInput.value = "";
        hideSearch();
      }
    });

    // Refresh
    els.btnRefresh.addEventListener("click", loadAll);

    // Modal
    els.modalClose.addEventListener("click", closeModal);
    els.modalOverlay.addEventListener("click", (e) => {
      if (e.target === els.modalOverlay) closeModal();
    });

    // Agent Tips toggle
    els.agentTipsHeader.addEventListener("click", toggleAgentTips);

    // Lightbox
    els.lightboxOverlay.addEventListener("click", closeLightbox);

    // Global keyboard
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (els.lightboxOverlay.classList.contains("open")) {
          closeLightbox();
        } else {
          closeModal();
        }
      }
    });

    // Initial load
    loadAll();

    // Polling
    pollTimer = setInterval(loadAll, POLL_INTERVAL_MS);
  }

  // ── Start ───────────────────────────────────────────────────────
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
