#!/usr/bin/env python3
"""
Telegram Commands für Git Federation Searcher
"""

import sys
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

sys.path.insert(0, '/root/.openclaw/workspace/skills/git-federation-searcher')
from git_federation_searcher import GitFederationSearcher, format_search_results


class GitSearchCommandHandler:
    """Telegram Commands für Git Federation Search"""
    
    def __init__(self):
        self.searcher = GitFederationSearcher()
    
    async def gitsearch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/gitsearch [query] - Suche in Git-Instanzen"""
        if not context.args:
            await update.message.reply_text(
                "🔍 **Git-Federation Suche**\n\n"
                "Nutzung:\n"
                "`/gitsearch whisper`\n"
                "`/gitsearch python telegram bot`\n\n"
                "Untersucht:\n"
                "• Codeberg.org\n"
                "• Gitea.com\n"
                "• NotABug.org\n"
                "• Gitdab.com\n\n"
                "Weitere:\n"
                "`/gitinstances` - Alle Instanzen\n"
                "`/gitadd Name URL Typ` - Instanz hinzufügen",
                parse_mode='Markdown'
            )
            return
        
        query = " ".join(context.args)
        processing = await update.message.reply_text(f"🔍 Suche nach \"{query}\" in Git-Instanzen...")
        
        try:
            results, stats = self.searcher.search_all(query, limit_per_instance=5)
            
            if results:
                text = format_search_results(results, query)
                text += f"\n📊 **{stats['total']} Ergebnisse** aus {len(stats['by_instance'])} Instanzen"
                
                await processing.edit_text(text, parse_mode='Markdown', disable_web_page_preview=True)
            else:
                # Fallback to web search
                await processing.edit_text("🌐 Keine API-Ergebnisse, versuche Web-Suche...")
                web_results = self.searcher._web_search(query)
                
                if web_results:
                    text = f"🌐 **Web-Ergebnisse für \"{query}\"**\n\n"
                    for r in web_results[:5]:
                        text += f"• [{r['name']}]({r['url']})\n"
                        text += f"  _{r.get('description', 'Keine Beschreibung')[:80]}..._\n\n"
                    
                    await processing.edit_text(text, parse_mode='Markdown', disable_web_page_preview=True)
                else:
                    await processing.edit_text(f"❌ Keine Ergebnisse für \"{query}\"")
                    
        except Exception as e:
            await processing.edit_text(f"❌ Fehler: {str(e)}")
    
    async def gitinstances_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/gitinstances - Liste alle Git-Instanzen"""
        try:
            instances = self.searcher.list_instances()
            
            text = "🌍 **Git-Instanzen**\n\n"
            
            for inst in instances:
                status = "✅" if inst["enabled"] else "❌"
                reachable = inst["status"]
                text += f"{status} **{inst['name']}** ({inst['type']})\n"
                text += f"   `{inst['url']}`\n"
                text += f"   Erreichbar: {reachable}\n\n"
            
            text += "💡 `/gitadd Name URL Typ` um neue hinzuzufügen"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Fehler: {str(e)}")
    
    async def gitadd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/gitadd [name] [url] [type] - Füge Git-Instanz hinzu"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "➕ **Git-Instanz hinzufügen**\n\n"
                "Nutzung:\n"
                "`/gitadd MyGitea https://git.example.com gitea`\n"
                "`/gitadd WorkGit https://gitlab.company.com gitlab`\n\n"
                "Typen: `gitea`, `gitlab`, `forgejo`",
                parse_mode='Markdown'
            )
            return
        
        name, url, inst_type = context.args[0], context.args[1], context.args[2]
        processing = await update.message.reply_text(f"➕ Teste {name}...")
        
        try:
            if self.searcher.add_instance(name, url, inst_type):
                await processing.edit_text(f"✅ Instanz '{name}' hinzugefügt!\n\nURL: {url}\nTyp: {inst_type}")
            else:
                await processing.edit_text(f"❌ Konnte '{name}' nicht erreichen.\nPrüfe URL und API-Verfügbarkeit.")
        except Exception as e:
            await processing.edit_text(f"❌ Fehler: {str(e)}")


def get_gitsearch_handlers():
    """Gibt alle Handler zurück"""
    handler = GitSearchCommandHandler()
    
    return [
        CommandHandler('gitsearch', handler.gitsearch_command),
        CommandHandler('gitinstances', handler.gitinstances_command),
        CommandHandler('gitadd', handler.gitadd_command),
    ]
