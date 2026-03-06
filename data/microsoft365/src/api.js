// custom-ms/src/api.js
const { getAccessToken } = require('./auth');
const { normalizeAccount } = require('./config');

const GRAPH_BASE = 'https://graph.microsoft.com/v1.0';

// Default account for backward compatibility if not specified
let currentAccount = 'default';

function setAccount(account) {
  currentAccount = normalizeAccount(account);
}

async function callGraph(endpoint, method = 'GET', body = null) {
  const token = await getAccessToken(currentAccount);
  if (!token) throw new Error('No access token available. Login required.');

  const headers = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const url = endpoint.startsWith('http') ? endpoint : `${GRAPH_BASE}${endpoint}`;
  const res = await fetch(url, options);

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Graph API Error (${res.status}): ${errText}`);
  }

  // Some endpoints return 204 No Content or 202 Accepted
  if (res.status === 204 || res.status === 202) return null;

  try {
    return await res.json();
  } catch (e) {
    return null;
  }
}

async function callGraphAllPages(endpoint) {
  let next = endpoint;
  const all = [];

  while (next) {
    const data = await callGraph(next);
    if (Array.isArray(data?.value)) all.push(...data.value);
    next = data?.['@odata.nextLink'] || null;
  }

  return all;
}

// === Email ===
async function getEmails(top = 10, { includeAllFolders = true } = {}) {
  const select = '$select=id,subject,from,receivedDateTime,isRead,bodyPreview,parentFolderId';

  // /me/messages is mailbox-breed en ondersteunt server-side sortering/filtering.
  if (!includeAllFolders) {
    const query = `?$top=${top}&${select}&$orderby=receivedDateTime desc`;
    const res = await callGraph(`/me/messages${query}`);
    return res?.value || [];
  }

  // Haal meerdere pagina's op voor een betrouwbare set uit alle folders en beperk daarna lokaal.
  const pageSize = Math.max(top, 25);
  const endpoint = `/me/messages?$top=${pageSize}&${select}&$orderby=receivedDateTime desc`;
  const messages = await callGraphAllPages(endpoint);
  return messages
    .sort((a, b) => new Date(b.receivedDateTime) - new Date(a.receivedDateTime))
    .slice(0, top);
}

async function searchEmails(query, { top = 25, includeAllFolders = true } = {}) {
  const safeQuery = String(query || '').replace(/'/g, "''");
  const select = '$select=id,subject,from,receivedDateTime,isRead,bodyPreview,parentFolderId';
  const searchParam = `$search="${safeQuery}"`;

  const endpoint = `/me/messages?${searchParam}&$top=${Math.max(top, 25)}&${select}`;

  if (!includeAllFolders) {
    const res = await callGraph(endpoint);
    return (res?.value || []).slice(0, top);
  }

  const all = await callGraphAllPages(endpoint);
  return all.slice(0, top);
}

async function sendEmail(to, subject, content) {
  const message = {
    message: {
      subject,
      body: {
        contentType: 'Text',
        content
      },
      toRecipients: [{ emailAddress: { address: to } }]
    }
  };
  return await callGraph('/me/sendMail', 'POST', message);
}

// === Calendar ===
async function listCalendars() {
  const calendars = await callGraphAllPages('/me/calendars?$select=id,name,color,canEdit,isDefaultCalendar');
  return calendars;
}

async function getCalendarEvents(days = 7, { includeAllCalendars = true, topPerCalendar = 100 } = {}) {
  const start = new Date().toISOString();
  const end = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
  const filter = `$filter=start/dateTime ge '${start}' and end/dateTime le '${end}'`;
  const select = '$select=id,subject,start,end,location,calendar';

  if (!includeAllCalendars) {
    const query = `?${filter}&${select}&$top=${topPerCalendar}`;
    const res = await callGraph(`/me/calendar/events${query}`);
    return res?.value || [];
  }

  const calendars = await listCalendars();
  const events = [];

  for (const cal of calendars) {
    const endpoint = `/me/calendars/${cal.id}/events?${filter}&${select}&$top=${topPerCalendar}`;
    const calEvents = await callGraphAllPages(endpoint);

    for (const event of calEvents) {
      events.push({
        ...event,
        calendar: event.calendar || { id: cal.id, name: cal.name }
      });
    }
  }

  return events.sort((a, b) => new Date(a.start?.dateTime || 0) - new Date(b.start?.dateTime || 0));
}

async function createEvent(subject, startStr, endStr, location, { calendarId = null } = {}) {
  const event = {
    subject,
    body: {
      contentType: 'HTML',
      content: 'Created via Custom MS Agent'
    },
    start: {
      dateTime: startStr,
      timeZone: 'UTC'
    },
    end: {
      dateTime: endStr,
      timeZone: 'UTC'
    },
    location: {
      displayName: location
    }
  };

  const endpoint = calendarId ? `/me/calendars/${calendarId}/events` : '/me/events';
  return await callGraph(endpoint, 'POST', event);
}

async function updateEvent(eventId, updates, { calendarId = null } = {}) {
  const endpoint = calendarId
    ? `/me/calendars/${calendarId}/events/${eventId}`
    : `/me/events/${eventId}`;
  return await callGraph(endpoint, 'PATCH', updates);
}

// === Contacts ===
async function getContactFoldersRecursive() {
  const folders = [];

  async function walk(folderId = null) {
    const endpoint = folderId
      ? `/me/contactFolders/${folderId}/childFolders?$select=id,displayName,parentFolderId`
      : '/me/contactFolders?$select=id,displayName,parentFolderId';

    const currentLevel = await callGraphAllPages(endpoint);
    for (const folder of currentLevel) {
      folders.push(folder);
      await walk(folder.id);
    }
  }

  await walk(null);
  return folders;
}

async function getContacts(top = 20, { includeAllFolders = true } = {}) {
  const select = '$select=id,displayName,emailAddresses,mobilePhone,parentFolderId';

  if (!includeAllFolders) {
    const res = await callGraph(`/me/contacts?$top=${top}&${select}`);
    return res?.value || [];
  }

  const byId = new Map();

  // Root/default contacts
  const rootContacts = await callGraphAllPages(`/me/contacts?$top=${Math.max(top, 100)}&${select}`);
  for (const c of rootContacts) byId.set(c.id, c);

  // Contacts in all folders (incl. mobile sync folders)
  const folders = await getContactFoldersRecursive();
  for (const folder of folders) {
    const folderContacts = await callGraphAllPages(
      `/me/contactFolders/${folder.id}/contacts?$top=${Math.max(top, 100)}&${select}`
    );

    for (const c of folderContacts) {
      byId.set(c.id, { ...c, folder: { id: folder.id, displayName: folder.displayName } });
    }
  }

  return Array.from(byId.values()).slice(0, top);
}

async function createContact(displayName, email, mobilePhone, { folderId = null } = {}) {
  const contact = {
    displayName,
    emailAddresses: email ? [{ address: email, name: displayName }] : [],
    mobilePhone
  };

  const endpoint = folderId ? `/me/contactFolders/${folderId}/contacts` : '/me/contacts';
  return await callGraph(endpoint, 'POST', contact);
}

async function updateContact(contactId, updates) {
  return await callGraph(`/me/contacts/${contactId}`, 'PATCH', updates);
}

// === OneDrive ===
async function listDriveRoot() {
  const res = await callGraph('/me/drive/root/children?$select=id,name,size,webUrl,folder,file,parentReference');
  return res?.value || [];
}

async function listDriveChildrenRecursive(folderId = 'root') {
  const allItems = [];

  async function walk(id) {
    const endpoint =
      id === 'root'
        ? '/me/drive/root/children?$select=id,name,size,webUrl,folder,file,parentReference'
        : `/me/drive/items/${id}/children?$select=id,name,size,webUrl,folder,file,parentReference`;

    const children = await callGraphAllPages(endpoint);
    for (const item of children) {
      allItems.push(item);
      if (item.folder) {
        await walk(item.id);
      }
    }
  }

  await walk(folderId);
  return allItems;
}

async function searchDrive(query, { recursive = true, folderId = 'root' } = {}) {
  const safeQuery = String(query || '').toLowerCase();

  if (!recursive && folderId === 'root') {
    const res = await callGraph(
      `/me/drive/root/search(q='${String(query || '').replace(/'/g, "''")}')?$select=id,name,webUrl,parentReference,file,folder`
    );
    return res?.value || [];
  }

  const items = await listDriveChildrenRecursive(folderId);
  return items.filter((item) => (item.name || '').toLowerCase().includes(safeQuery));
}

async function uploadFile(fileName, content) {
  const endpoint = `/me/drive/root:/${fileName}:/content`;
  const token = await getAccessToken(currentAccount);

  const res = await fetch(`https://graph.microsoft.com/v1.0${endpoint}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'text/plain'
    },
    body: content
  });

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.statusText}`);
  }

  return await res.json();
}

module.exports = {
  setAccount,
  getEmails,
  searchEmails,
  sendEmail,
  listCalendars,
  getCalendarEvents,
  createEvent,
  updateEvent,
  getContacts,
  createContact,
  updateContact,
  listDriveRoot,
  listDriveChildrenRecursive,
  searchDrive,
  uploadFile
};
