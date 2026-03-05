// ChatGPT Full Export Bookmarklet v2.0
// Now exports conversations inside Projects (folders) too!
// Paste this entire script in Chrome DevTools console while on chatgpt.com
// It will download all conversations as a single JSON file

(async function () {
  console.log("🚀 ChatGPT Exporter v2.0 starting...");

  // Get access token
  console.log("🔑 Getting access token...");
  const sessionResp = await fetch("/api/auth/session", { credentials: "include" });
  const { accessToken } = await sessionResp.json();

  if (!accessToken) {
    alert("❌ Not logged in! Please log into ChatGPT first.");
    return;
  }

  const headers = { Authorization: `Bearer ${accessToken}` };

  // Phase 1: Fetch conversation IDs from the main listing endpoint
  console.log("📋 Phase 1: Fetching main conversation list...");
  const allIds = new Map(); // id -> { title, create_time }
  let offset = 0;
  const limit = 100;

  while (true) {
    const resp = await fetch(`/backend-api/conversations?offset=${offset}&limit=${limit}`, {
      headers,
    });
    const data = await resp.json();
    for (const item of data.items) {
      allIds.set(item.id, { title: item.title, create_time: item.create_time });
    }
    console.log(`   Listed ${allIds.size} conversations...`);
    if (data.items.length < limit) break;
    offset += limit;
    await new Promise((r) => setTimeout(r, 200));
  }

  const listedCount = allIds.size;
  console.log(`📊 Main listing: ${listedCount} conversations`);

  // Phase 2: Search-based discovery to find conversations inside Projects/folders
  console.log("🔍 Phase 2: Searching for conversations in Projects...");
  const searchTerms = [
    // Common words in multiple languages to maximize coverage
    "a",
    "e",
    "i",
    "o",
    "u",
    "el",
    "la",
    "de",
    "que",
    "per",
    "com",
    "en",
    "es",
    "un",
    "una",
    "the",
    "is",
    "to",
    "and",
    "for",
    "how",
    "what",
    "can",
    "my",
    "new",
    "AI",
    "code",
    "python",
    "help",
    "project",
    "plan",
    "mail",
    "work",
    "home",
    "casa",
    "buy",
    "water",
    "make",
    "create",
    "fix",
    "error",
    "list",
    "write",
    "find",
    "get",
    "set",
    "add",
    "use",
    "run",
    "file",
    "data",
    "test",
    "build",
    "open",
    "send",
    "read",
    "show",
    "app",
    "web",
    "api",
    "key",
    "log",
    "config",
    "install",
    "update",
  ];

  for (const term of searchTerms) {
    try {
      const resp = await fetch(
        `/backend-api/conversations/search?query=${encodeURIComponent(term)}&limit=50`,
        { headers },
      );
      const data = await resp.json();
      for (const item of data.items || []) {
        if (!allIds.has(item.conversation_id)) {
          allIds.set(item.conversation_id, {
            title: item.title,
            create_time: null, // will be filled when fetching full conversation
            source: "project",
          });
        }
      }
    } catch (e) {
      // search term returned error, skip
    }
    await new Promise((r) => setTimeout(r, 100));
  }

  const projectCount = allIds.size - listedCount;
  console.log(`🔍 Found ${projectCount} additional conversations in Projects`);
  console.log(`📊 Total: ${allIds.size} conversations`);

  // Phase 3: Fetch each conversation's full content
  console.log("📥 Phase 3: Fetching full conversations...");
  const results = [];
  const errors = [];
  let idx = 0;
  const total = allIds.size;

  for (const [convId, meta] of allIds) {
    idx++;
    const progress = `[${idx}/${total}]`;

    try {
      const resp = await fetch(`/backend-api/conversation/${convId}`, { headers });

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const data = await resp.json();

      // Extract messages from mapping tree
      const messages = [];
      for (const node of Object.values(data.mapping || {})) {
        if (node.message?.content?.parts && node.message.author?.role !== "system") {
          const textParts = node.message.content.parts.filter((p) => typeof p === "string");
          if (textParts.length > 0) {
            messages.push({
              role: node.message.author.role,
              text: textParts.join("\n"),
              time: node.message.create_time || 0,
            });
          }
        }
      }
      messages.sort((a, b) => a.time - b.time);

      results.push({
        id: convId,
        title: data.title || meta.title || "Untitled",
        created: data.create_time,
        updated: data.update_time,
        gizmo_id: data.gizmo_id || null,
        messages,
      });

      console.log(`✅ ${progress} ${data.title || "Untitled"}`);
    } catch (e) {
      console.error(`❌ ${progress} Error: ${e.message}`);
      errors.push({ id: convId, title: meta.title, error: e.message });
    }

    // Rate limiting
    if (idx < total) {
      await new Promise((r) => setTimeout(r, 100));
    }
  }

  // Create download
  console.log("📦 Creating download...");

  const exportData = {
    exported: new Date().toISOString(),
    exporter_version: "2.0",
    total: allIds.size,
    listed: listedCount,
    from_projects: projectCount,
    successful: results.length,
    errors: errors.length,
    conversations: results,
    failedConversations: errors,
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `chatgpt-export-${new Date().toISOString().split("T")[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  console.log("");
  console.log("🎉 Export complete!");
  console.log(`   📋 Listed: ${listedCount}`);
  console.log(`   🔍 From Projects: ${projectCount}`);
  console.log(`   ✅ Exported: ${results.length}`);
  console.log(`   ❌ Errors: ${errors.length}`);
  console.log("   📁 Check your Downloads folder");

  alert(
    `✅ Export complete!\n\nListed: ${listedCount}\nFrom Projects: ${projectCount}\nExported: ${results.length}\nErrors: ${errors.length}\n\nCheck your Downloads folder.`,
  );
})();
