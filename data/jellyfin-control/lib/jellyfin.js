const axios = require('axios');

// Configuration
const CONFIG = {
    url: process.env.JF_URL || 'http://localhost:8096',
    apiKey: process.env.JF_API_KEY,
    user: process.env.JF_USER,
    pass: process.env.JF_PASS, // New
    userId: process.env.JF_USER_ID || null,
    deviceName: 'OpenClaw',
    deviceId: 'openclaw-skill-001',
    clientVersion: '1.0.0'
};

if (!CONFIG.apiKey && !CONFIG.pass) {
    console.error('Error: JF_API_KEY or JF_USER+JF_PASS environment variables are required.');
    process.exit(1);
}

// Axios instance
const api = axios.create({
    baseURL: CONFIG.url,
    headers: {
        'X-Emby-Token': CONFIG.apiKey, // Default to API Key
        'X-Emby-Authorization': `MediaBrowser Client="${CONFIG.deviceName}", Device="${CONFIG.deviceName}", DeviceId="${CONFIG.deviceId}", Version="${CONFIG.clientVersion}"`,
        'Content-Type': 'application/json'
    }
});

const handleErr = (context, err) => {
    if (err.response) {
        console.error(`❌ [${context}] Error ${err.response.status}: ${err.response.statusText}`);
        if (err.response.data) console.error('Details:', JSON.stringify(err.response.data));
    } else {
        console.error(`❌ [${context}] Error: ${err.message}`);
    }
    process.exit(1);
};

// 0. Login (Upgrade to User Session)
let sessionToken = null;
async function login() {
    if (sessionToken) return sessionToken;
    if (!CONFIG.user || !CONFIG.pass) return CONFIG.apiKey;

    try {
        const res = await api.post('/Users/AuthenticateByName', {
            Username: CONFIG.user,
            Pw: CONFIG.pass
        });
        
        sessionToken = res.data.AccessToken;
        CONFIG.userId = res.data.User.Id;
        api.defaults.headers['X-Emby-Token'] = sessionToken; // Upgrade headers
        // console.log('🔑 Logged in via User/Pass');
        return sessionToken;
    } catch (e) {
        // console.warn('⚠️ Login failed, staying with API Key.');
        return CONFIG.apiKey;
    }
}

// 1. Get User ID
async function getUserId(targetUsername) {
    // Ensure we have max privileges
    await login();

    // If searching for someone else
    if (targetUsername) {
        try {
            const res = await api.get('/Users');
            const u = res.data.find(u => u.Name.toLowerCase() === targetUsername.toLowerCase());
            if (u) return u.Id;
            console.error(`❌ User '${targetUsername}' not found.`);
            process.exit(1);
        } catch (e) { handleErr('getUserId (search)', e); }
    }

    // Default: Current User
    if (CONFIG.userId) return CONFIG.userId;

    try {
        const me = await api.get('/Users/Me');
        if (me.data && me.data.Id) {
            CONFIG.userId = me.data.Id;
            return me.data.Id;
        }
    } catch (e) {}

    console.error('❌ Could not determine User ID.');
    process.exit(1);
}

// 2. Search Item
async function searchItem(query, type = 'Series,Movie') {
    try {
        const userId = await getUserId();
        const res = await api.get('/Items', {
            params: {
                SearchTerm: query,
                IncludeItemTypes: type,
                Recursive: true,
                UserId: userId,
                Limit: 5
            }
        });
        return res.data.Items;
    } catch (e) { handleErr('searchItem', e); }
}

// 3. Get Next Episode
async function getNextEpisode(seriesId) {
    const userId = await getUserId();
    
    try {
        const nextUp = await api.get('/Shows/NextUp', {
            params: { SeriesId: seriesId, UserId: userId, Limit: 1 }
        });
        if (nextUp.data.Items.length > 0) return nextUp.data.Items[0];
    } catch (e) {}

    try {
        const unplayed = await api.get('/Items', {
            params: {
                ParentId: seriesId,
                Recursive: true,
                IncludeItemTypes: 'Episode',
                SortBy: 'SortName',
                SortOrder: 'Ascending',
                Filters: 'IsUnplayed',
                Limit: 1,
                UserId: userId
            }
        });
        if (unplayed.data.Items.length > 0) return unplayed.data.Items[0];
    } catch (e) { handleErr('getNextEpisode', e); }

    // Fallback: Last episode (Rewatch)
    try {
        const lastEp = await api.get('/Items', {
            params: {
                ParentId: seriesId,
                Recursive: true,
                IncludeItemTypes: 'Episode',
                SortBy: 'SortName', 
                SortOrder: 'Descending',
                Limit: 1,
                UserId: userId
            }
        });
        if (lastEp.data.Items.length > 0) return lastEp.data.Items[0];
    } catch (e) {}

    return null;
}

// 4. Find Session
async function findSession(targetDeviceName) {
    await login();
    try {
        const res = await api.get('/Sessions');
        const sessions = res.data;
        const controllable = sessions.filter(s => s.SupportsRemoteControl);

        if (controllable.length === 0) return null;

        if (targetDeviceName) {
            const match = controllable.find(s => 
                (s.DeviceName && s.DeviceName.toLowerCase().includes(targetDeviceName.toLowerCase())) ||
                (s.Client && s.Client.toLowerCase().includes(targetDeviceName.toLowerCase()))
            );
            return match || null;
        }

        return controllable.sort((a, b) => new Date(b.LastActivityDate) - new Date(a.LastActivityDate))[0];
    } catch (e) { handleErr('findSession', e); }
}

// 5. Play Item
async function playItem(sessionId, itemId, startTicks = 0) {
    await login();
    try {
        await api.post(`/Sessions/${sessionId}/Playing`, null, {
            params: {
                ItemIds: itemId,
                PlayCommand: 'PlayNow',
                StartPositionTicks: startTicks
            }
        });

        if (startTicks > 0) {
            await new Promise(r => setTimeout(r, 2000));
            await api.post(`/Sessions/${sessionId}/Playing/Seek`, null, {
                params: { SeekPositionTicks: startTicks }
            });
            console.log(`⏱️ Enforced seek to ${Math.floor(startTicks/10000000)}s`);
        }
        return true;
    } catch (e) { handleErr('playItem', e); }
}

// 6. Control Session
async function controlSession(sessionId, action, value) {
    await login();
    try {
        let endpoint = `/Sessions/${sessionId}/Playing`;
        let command = '';
        let params = {};

        switch (action.toLowerCase()) {
            case 'play':
            case 'unpause': command = 'Unpause'; break;
            case 'pause': command = 'Pause'; break;
            case 'playpause': command = 'PlayPause'; break;
            case 'stop': command = 'Stop'; break;
            case 'next': command = 'NextTrack'; break;
            case 'prev': command = 'PreviousTrack'; break;
            case 'mute': endpoint = `/Sessions/${sessionId}/Command`; command = 'Mute'; break;
            case 'unmute': endpoint = `/Sessions/${sessionId}/Command`; command = 'Unmute'; break;
            case 'volup': endpoint = `/Sessions/${sessionId}/Command`; command = 'VolumeUp'; break;
            case 'voldown': endpoint = `/Sessions/${sessionId}/Command`; command = 'VolumeDown'; break;
            case 'vol':
            case 'volume':
                endpoint = `/Sessions/${sessionId}/Command`;
                command = 'SetVolume';
                params = { Arguments: value };
                break;
            default: throw new Error(`Unknown action: ${action}`);
        }

        endpoint += `/${command}`;
        await api.post(endpoint, params);
        return true;
    } catch (e) { handleErr('controlSession', e); }
}

// 7. Get User History
async function getUserHistory(username, days = 7) {
    // Need admin rights to search other users
    await login(); 
    
    try {
        const targetUserId = await getUserId(username);
        
        const dateLimit = new Date();
        dateLimit.setDate(dateLimit.getDate() - days);

        const log = await api.get('/System/ActivityLog/Entries', {
            params: {
                MinDate: dateLimit.toISOString(),
                Limit: 100
            }
        });

        // Filter by user ID
        const entries = log.data.Items.filter(e => e.UserId === targetUserId);

        return entries.map(e => ({
            date: e.Date,
            name: e.Name,
            type: e.Type,
            severity: e.Severity,
            shortDate: new Date(e.Date).toLocaleString()
        }));

    } catch (e) { handleErr('getUserHistory', e); }
}

// 8. Get Statistics
async function getStats() {
    await login();
    try {
        const counts = await api.get('/Items/Counts');
        return {
            movies: counts.data.MovieCount,
            series: counts.data.SeriesCount,
            episodes: counts.data.EpisodeCount,
            songs: counts.data.SongCount
        };
    } catch (e) { handleErr('getStats', e); }
}

// 9. Refresh Library
async function refreshLibrary() {
    await login();
    try {
        await api.post('/Library/Refresh');
        return true;
    } catch (e) { handleErr('refreshLibrary', e); }
}

module.exports = {
    CONFIG,
    searchItem,
    getNextEpisode,
    findSession,
    playItem,
    controlSession,
    getUserHistory,
    getStats,
    refreshLibrary,
    getUserId
};
