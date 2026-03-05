/**
 * ClawArcade Leaderboard System
 * Include this script in any game to enable leaderboard functionality
 */

(function() {
    'use strict';

    const ClawArcade = {
        // ==================== STORAGE ====================
        getKey: (gameId) => `clawarcade_lb_${gameId}`,
        
        getScores: function(gameId) {
            const data = localStorage.getItem(this.getKey(gameId));
            return data ? JSON.parse(data) : [];
        },
        
        addScore: function(gameId, name, score) {
            const scores = this.getScores(gameId);
            scores.push({ name, score, date: Date.now() });
            scores.sort((a, b) => b.score - a.score);
            const top10 = scores.slice(0, 10);
            localStorage.setItem(this.getKey(gameId), JSON.stringify(top10));
            return top10;
        },
        
        getHighScore: function(gameId) {
            const scores = this.getScores(gameId);
            return scores.length > 0 ? scores[0].score : 0;
        },
        
        getUsername: function() {
            return localStorage.getItem('clawmd_username') || 'Anonymous';
        },

        // ==================== SUBMIT SCORE ====================
        submitScore: function(gameId, score) {
            const username = this.getUsername();
            this.addScore(gameId, username, score);
            return this.getScores(gameId);
        },

        // ==================== UI COMPONENTS ====================
        
        // Inject styles for leaderboard components
        injectStyles: function() {
            if (document.getElementById('clawarcade-lb-styles')) return;
            
            const style = document.createElement('style');
            style.id = 'clawarcade-lb-styles';
            style.textContent = `
                .clawarcade-lb-modal {
                    position: fixed;
                    top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0, 0, 0, 0.9);
                    display: none;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    animation: lbFadeIn 0.3s;
                }
                .clawarcade-lb-modal.active { display: flex; }
                @keyframes lbFadeIn { from { opacity: 0; } to { opacity: 1; } }
                
                .clawarcade-lb-box {
                    background: linear-gradient(135deg, #1a0030 0%, #0d001a 100%);
                    border: 2px solid #00ffff;
                    border-radius: 16px;
                    padding: 1.5rem;
                    max-width: 350px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 0 40px rgba(0, 255, 255, 0.4);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
                
                .clawarcade-lb-title {
                    color: #00ffff;
                    text-align: center;
                    margin-bottom: 1rem;
                    font-size: 1.3rem;
                    text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
                }
                
                .clawarcade-lb-score-display {
                    text-align: center;
                    margin-bottom: 1rem;
                }
                
                .clawarcade-lb-score-label {
                    color: #888;
                    font-size: 0.9rem;
                }
                
                .clawarcade-lb-score-value {
                    color: #00ff88;
                    font-size: 2.5rem;
                    font-weight: bold;
                    text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
                }
                
                .clawarcade-lb-newrecord {
                    color: #ffdd00;
                    font-size: 0.9rem;
                    animation: lbPulse 1s infinite;
                }
                @keyframes lbPulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                .clawarcade-lb-list {
                    list-style: none;
                    padding: 0;
                    margin: 0 0 1rem 0;
                }
                
                .clawarcade-lb-item {
                    display: flex;
                    align-items: center;
                    padding: 0.6rem 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    gap: 0.75rem;
                }
                
                .clawarcade-lb-item.highlight {
                    background: rgba(0, 255, 136, 0.1);
                    border-radius: 8px;
                    padding: 0.6rem;
                    margin: 0 -0.5rem;
                }
                
                .clawarcade-lb-rank {
                    min-width: 30px;
                    font-weight: bold;
                    color: #ff00ff;
                }
                .clawarcade-lb-rank.gold { color: #ffdd00; }
                .clawarcade-lb-rank.silver { color: #c0c0c0; }
                .clawarcade-lb-rank.bronze { color: #cd7f32; }
                
                .clawarcade-lb-name {
                    flex: 1;
                    color: #fff;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                .clawarcade-lb-points {
                    color: #00ff88;
                    font-weight: bold;
                }
                
                .clawarcade-lb-empty {
                    text-align: center;
                    color: rgba(255, 255, 255, 0.5);
                    padding: 1.5rem;
                }
                
                .clawarcade-lb-buttons {
                    display: flex;
                    gap: 0.5rem;
                    flex-wrap: wrap;
                }
                
                .clawarcade-lb-btn {
                    flex: 1;
                    min-width: 100px;
                    padding: 0.75rem;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    font-size: 0.9rem;
                    transition: all 0.2s;
                    border: 2px solid;
                }
                
                .clawarcade-lb-btn.primary {
                    background: linear-gradient(135deg, #ff00ff 0%, #00ffff 100%);
                    border-color: transparent;
                    color: #000;
                }
                
                .clawarcade-lb-btn.secondary {
                    background: transparent;
                    border-color: #00ffff;
                    color: #00ffff;
                }
                
                .clawarcade-lb-btn.share {
                    background: #000;
                    border-color: #333;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.5rem;
                }
                
                .clawarcade-lb-btn:hover {
                    transform: scale(1.03);
                    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
                }
                
                .clawarcade-lb-btn:active {
                    transform: scale(0.97);
                }
            `;
            document.head.appendChild(style);
        },

        // Create and show the leaderboard modal after game over
        showGameOverModal: function(gameId, gameName, score, options = {}) {
            this.injectStyles();
            
            const username = this.getUsername();
            const previousHigh = this.getHighScore(gameId);
            const isNewRecord = score > previousHigh;
            
            // Submit score
            const scores = this.submitScore(gameId, score);
            
            // Find player's rank
            const playerRank = scores.findIndex(s => s.score === score && s.name === username) + 1;
            
            // Create modal
            let modal = document.getElementById('clawarcade-lb-modal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'clawarcade-lb-modal';
                modal.className = 'clawarcade-lb-modal';
                document.body.appendChild(modal);
            }
            
            const listHtml = scores.length === 0 
                ? '<li class="clawarcade-lb-empty">No scores yet!</li>'
                : scores.map((s, i) => {
                    const rankClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
                    const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
                    const highlight = s.score === score && s.name === username ? 'highlight' : '';
                    return `
                        <li class="clawarcade-lb-item ${highlight}">
                            <span class="clawarcade-lb-rank ${rankClass}">${medal}</span>
                            <span class="clawarcade-lb-name">${s.name}</span>
                            <span class="clawarcade-lb-points">${s.score.toLocaleString()}</span>
                        </li>
                    `;
                }).join('');
            
            modal.innerHTML = `
                <div class="clawarcade-lb-box">
                    <h2 class="clawarcade-lb-title">🎮 Game Over!</h2>
                    <div class="clawarcade-lb-score-display">
                        <div class="clawarcade-lb-score-label">Your Score</div>
                        <div class="clawarcade-lb-score-value">${score.toLocaleString()}</div>
                        ${isNewRecord ? '<div class="clawarcade-lb-newrecord">🎉 NEW PERSONAL BEST!</div>' : ''}
                    </div>
                    <h3 style="color:#ffaa00;margin-bottom:0.5rem;font-size:1rem;">🏆 Leaderboard</h3>
                    <ul class="clawarcade-lb-list">${listHtml}</ul>
                    <div class="clawarcade-lb-buttons">
                        <button class="clawarcade-lb-btn primary" onclick="ClawArcade.closeModal(); ${options.onPlayAgain || 'location.reload()'}">Play Again</button>
                        <button class="clawarcade-lb-btn secondary" onclick="window.location.href='../index.html'">Home</button>
                    </div>
                    <div class="clawarcade-lb-buttons" style="margin-top:0.5rem;">
                        <button class="clawarcade-lb-btn share" onclick="ClawArcade.shareScore('${gameId}', '${gameName}', ${score})">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                            Share on X
                        </button>
                    </div>
                </div>
            `;
            
            modal.classList.add('active');
            
            // Close on backdrop click
            modal.onclick = (e) => {
                if (e.target === modal) this.closeModal();
            };
        },

        closeModal: function() {
            const modal = document.getElementById('clawarcade-lb-modal');
            if (modal) modal.classList.remove('active');
        },

        shareScore: function(gameId, gameName, score) {
            const text = encodeURIComponent(`I scored ${score.toLocaleString()} on ${gameName} at ClawArcade! 🎮 Can you beat me? clawarcade.surge.sh/games/${gameId}.html #ClawArcade`);
            window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank', 'width=550,height=420');
        },

        // Simple inline leaderboard (can be embedded in game UI)
        createInlineLeaderboard: function(gameId, containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;
            
            const scores = this.getScores(gameId);
            
            if (scores.length === 0) {
                container.innerHTML = '<div style="color:#888;font-size:0.8rem;text-align:center;">No scores yet!</div>';
                return;
            }
            
            container.innerHTML = scores.slice(0, 5).map((s, i) => {
                const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`;
                return `<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.1);font-size:0.8rem;">
                    <span style="color:#ff00ff;">${medal}</span>
                    <span style="color:#fff;flex:1;margin:0 0.5rem;overflow:hidden;text-overflow:ellipsis;">${s.name}</span>
                    <span style="color:#00ff88;">${s.score}</span>
                </div>`;
            }).join('');
        }
    };

    // Expose globally
    window.ClawArcade = ClawArcade;
})();
