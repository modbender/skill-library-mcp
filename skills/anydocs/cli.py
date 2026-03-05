"""Click-based CLI for anydocs."""

import click
import logging
from pathlib import Path
from lib.config import ConfigManager
from lib.cache import CacheManager
from lib.scraper import DiscoveryEngine
from lib.indexer import SearchIndex


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AnyDocsConfig:
    """CLI context object."""
    def __init__(self):
        self.config_mgr = ConfigManager()
        self.cache_mgr = CacheManager()


@click.group()
@click.pass_context
def cli(ctx):
    """anydocs - Generic documentation indexing and search.

    Works with ANY documentation site. Configure profiles, index docs, and search.

    Examples:
        anydocs config discord https://discord.com/developers/docs https://discord.com/developers/docs/sitemap
        anydocs index discord
        anydocs search "webhook" --profile discord
    """
    ctx.ensure_object(AnyDocsConfig)


@cli.command()
@click.argument("profile")
@click.argument("base_url")
@click.argument("sitemap_url")
@click.option("--search-method", default="hybrid",
              type=click.Choice(["keyword", "semantic", "hybrid"]),
              help="Search method: keyword, semantic, or hybrid")
@click.option("--ttl-days", default=7, type=int,
              help="Cache TTL in days")
@click.pass_context
def config(ctx, profile: str, base_url: str, sitemap_url: str,
           search_method: str, ttl_days: int):
    """Configure a documentation profile.

    PROFILE: Profile name (e.g., 'discord', 'openclaw', 'custom')
    BASE_URL: Base documentation URL
    SITEMAP_URL: Sitemap XML URL

    Example:
        anydocs config discord https://discord.com/developers/docs https://discord.com/developers/docs/sitemap
    """
    config_obj = ctx.obj
    try:
        config_obj.config_mgr.add_profile(profile, base_url, sitemap_url, search_method, ttl_days)
        click.secho(f"✓ Profile '{profile}' configured successfully", fg='green')
        click.echo(f"  Base URL: {base_url}")
        click.echo(f"  Sitemap: {sitemap_url}")
        click.echo(f"  Search method: {search_method}")
    except ValueError as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        raise click.Abort()


@cli.command()
@click.pass_context
def list_profiles(ctx):
    """List all configured profiles."""
    config_obj = ctx.obj
    profiles = config_obj.config_mgr.list_profiles()

    if not profiles:
        click.echo("No profiles configured yet.")
        click.echo("Use: anydocs config <profile> <base_url> <sitemap_url>")
        return

    click.echo("Configured profiles:")
    for profile in profiles:
        cfg = config_obj.config_mgr.get_profile(profile)
        click.echo(f"\n  {profile}")
        click.echo(f"    Base URL: {cfg['base_url']}")
        click.echo(f"    Sitemap: {cfg['sitemap_url']}")
        click.echo(f"    Search: {cfg.get('search_method', 'hybrid')}")


@cli.command()
@click.argument("profile")
@click.option("--force", is_flag=True, help="Skip cache and re-index")
@click.option("--use-browser", is_flag=True, help="Render JS-heavy pages with browser tool")
@click.option("--gateway-url", default=None, help="OpenClaw gateway URL (e.g., http://localhost:18789)")
@click.option("--gateway-token", default=None, help="OpenClaw gateway token (from $OPENCLAW_GATEWAY_TOKEN)")
@click.pass_context
def index(ctx, profile: str, force: bool, use_browser: bool, gateway_url: str, gateway_token: str):
    """Build search index for a profile.
    
    PROFILE: Profile to index

    Discovers all documentation pages via sitemap,
    scrapes content, and builds search index.
    
    Use --use-browser to enable JavaScript rendering for SPA docs (Discord, etc).
    
    Example:
        anydocs index discord
        anydocs index discord --use-browser --gateway-token YOUR_TOKEN
    """
    config_obj = ctx.obj
    is_valid, error = config_obj.config_mgr.validate_profile(profile)
    if not is_valid:
        click.secho(f"✗ {error}", fg='red', err=True)
        raise click.Abort()
    
    cfg = config_obj.config_mgr.get_profile(profile)
    
    # Check cache unless forced
    if not force:
        cached_index = config_obj.cache_mgr.get_index(profile, cfg["cache_ttl_days"])
        if cached_index:
            click.secho(f"✓ Using cached index for '{profile}'", fg='green')
            click.echo(f"  Documents: {cached_index['count']}")
            return
    
    click.echo(f"Indexing '{profile}'...")
    
    # Get gateway token from env if not provided
    if use_browser and not gateway_token:
        import os
        gateway_token = os.environ.get("OPENCLAW_GATEWAY_TOKEN", "")
    
    # Scrape
    engine = DiscoveryEngine(
        cfg["base_url"], 
        cfg["sitemap_url"],
        use_browser=use_browser,
        gateway_url=gateway_url or "http://127.0.0.1:18789",
        gateway_token=gateway_token
    )

    with click.progressbar(length=1, label="Discovering URLs") as bar:
        urls = engine.discover_urls()
        bar.update(1)

    click.echo(f"Found {len(urls)} pages to scrape")

    pages = []
    with click.progressbar(urls, label="Scraping pages") as bar:
        for url in bar:
            page = engine.scrape_page(url)
            if page:
                pages.append(page)
                config_obj.cache_mgr.save_page(url, page["title"], page["content"],
                                               {"tags": page.get("tags", [])})

    # Build index
    with click.progressbar(length=1, label="Building index") as bar:
        index_obj = SearchIndex()
        index_obj.build(pages)
        bar.update(1)

    # Cache index
    config_obj.cache_mgr.save_index(profile, index_obj.to_dict())

    click.secho(f"\n✓ Indexed {len(pages)} pages for '{profile}'", fg='green')


@cli.command()
@click.argument("query")
@click.option("--profile", default="discord",
              help="Profile to search (default: discord)")
@click.option("--limit", default=10, type=int,
              help="Maximum results (default: 10)")
@click.option("--regex", is_flag=True,
              help="Treat query as regex pattern")
@click.pass_context
def search(ctx, query: str, profile: str, limit: int, regex: bool):
    """Search documentation.

    QUERY: Search query

    Examples:
        anydocs search "webhooks" --profile discord
        anydocs search "rate limit" --profile discord --limit 5
        anydocs search "^API" --profile discord --regex
    """
    config_obj = ctx.obj
    is_valid, error = config_obj.config_mgr.validate_profile(profile)
    if not is_valid:
        click.secho(f"✗ {error}", fg='red', err=True)
        raise click.Abort()

    cfg = config_obj.config_mgr.get_profile(profile)

    # Load index from cache
    cached_index = config_obj.cache_mgr.get_index(profile, cfg["cache_ttl_days"])
    if not cached_index:
        click.secho(f"✗ No index for '{profile}'. Run: anydocs index {profile}", fg='red', err=True)
        raise click.Abort()

    # Perform search
    index_obj = SearchIndex.from_dict(cached_index)
    results = index_obj.search(query, method=cfg.get("search_method", "hybrid"),
                          limit=limit, regex=regex)

    if not results:
        click.echo(f"No results for: {query}")
        return

    click.secho(f"\nResults for: {query} ({len(results)} found)\n", fg='cyan', bold=True)

    for result in results:
        click.secho(f"[{result['rank']}] {result['title']}", fg='cyan', bold=True)
        click.echo(f"    URL: {result['url']}")
        click.echo(f"    Relevance: {result['relevance_score']}")
        if result.get('tags'):
            click.echo(f"    Tags: {', '.join(result['tags'][:5])}")
        # Show snippet
        content_preview = result['content'][:150].replace('\n', ' ')
        click.echo(f"    {content_preview}...")
        click.echo()


@cli.command()
@click.argument("path")
@click.option("--profile", default="discord",
              help="Profile to search in (default: discord)")
@click.pass_context
def fetch(ctx, path: str, profile: str):
    """Fetch a specific documentation page.

    PATH: Path or URL to fetch

    Examples:
        anydocs fetch "https://discord.com/developers/docs/resources/webhook"
        anydocs fetch "webhooks" --profile discord
    """
    config_obj = ctx.obj
    is_valid, error = config_obj.config_mgr.validate_profile(profile)
    if not is_valid:
        click.secho(f"✗ {error}", fg='red', err=True)
        raise click.Abort()

    cfg = config_obj.config_mgr.get_profile(profile)

    # Build full URL if path doesn't start with http
    if path.startswith("http"):
        url = path
    else:
        url = f"{cfg['base_url']}/{path.lstrip('/')}"

    # Try cache first
    cached_page = config_obj.cache_mgr.get_page(url, cfg["cache_ttl_days"])
    if cached_page:
        click.echo(f"Title: {cached_page['title']}\n")
        click.echo(cached_page['content'])
        return

    # Fetch fresh
    click.echo(f"Fetching {url}...")
    engine = DiscoveryEngine(cfg['base_url'], cfg['sitemap_url'])
    page = engine.scrape_page(url)

    if not page:
        click.secho(f"✗ Failed to fetch {url}", fg='red', err=True)
        raise click.Abort()

    click.echo(f"Title: {page['title']}\n")
    click.echo(page['content'])


@cli.group()
def cache():
    """Cache management commands."""
    pass


@cache.command(name="status")
@click.pass_context
def cache_status(ctx):
    """Show cache statistics."""
    config_obj = ctx.obj
    stats = config_obj.cache_mgr.get_cache_size()

    click.echo("Cache status:")
    click.echo(f"  Location: {stats['cache_dir']}")
    click.echo(f"  Pages cached: {stats['pages_count']}")
    click.echo(f"  Indexes cached: {stats['indexes_count']}")
    click.echo(f"  Total size: {stats['total_size_mb']} MB")


@cache.command(name="clear")
@click.option("--profile", default=None,
              help="Clear only this profile's cache")
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
@click.pass_context
def cache_clear(ctx, profile: str):
    """Clear the cache."""
    config_obj = ctx.obj
    deleted = config_obj.cache_mgr.clear_cache(profile)

    if profile:
        click.secho(f"✓ Cleared cache for '{profile}' ({deleted} files)", fg='green')
    else:
        click.secho(f"✓ Cleared all cache ({deleted} files)", fg='green')


if __name__ == "__main__":
    cli()
