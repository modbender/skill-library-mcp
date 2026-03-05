#![deny(clippy::unwrap_used)]
#![deny(clippy::expect_used)]
#![warn(clippy::pedantic)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::struct_excessive_bools)]

mod client;
mod protocol;
mod types;

use client::ExaClient;
use protocol::{format_results, Input, Output};
use std::io::{self, Read};
use types::{
    params::{ContentsInput, ExtrasOptions},
    ContentsOptions, FindSimilarOptions, GetContentsOptions, SearchOptions, TextOptions,
};

#[tokio::main]
async fn main() {
    // ── Read API key ─────────────────────────────────────────────────────────
    let api_key = match std::env::var("EXA_API_KEY") {
        Ok(k) if !k.is_empty() => k,
        _ => emit_err("EXA_API_KEY environment variable not set"),
    };
    if !is_valid_uuid(&api_key) {
        emit_err(
            "EXA_API_KEY is invalid: expected UUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)",
        );
    }

    // ── Read stdin ───────────────────────────────────────────────────────────
    let mut limited = io::stdin().take(1_048_577); // 1MB + 1 byte
    let mut buf = String::new();
    if let Err(e) = limited.read_to_string(&mut buf) {
        emit_err(&format!("Failed to read stdin: {e}"));
    }
    if buf.len() > 1_048_576 {
        emit_err("Input too large: maximum is 1MB");
    }

    // ── Parse input ──────────────────────────────────────────────────────────
    let input: Input = match serde_json::from_str(&buf) {
        Ok(i) => i,
        Err(e) => emit_err(&format!("Invalid JSON input: {e}")),
    };

    // ── Build client ─────────────────────────────────────────────────────────
    let client = match ExaClient::new(api_key) {
        Ok(c) => c,
        Err(e) => emit_err(&format!("Failed to create HTTP client: {e}")),
    };

    // ── Dispatch ─────────────────────────────────────────────────────────────
    let action = input.action.as_deref().unwrap_or("search");

    match action {
        "search" => handle_search(client, input).await,
        "find_similar" => handle_find_similar(client, input).await,
        "get_contents" => handle_get_contents(client, input).await,
        other => emit_err(&format!("Unknown action: {other}")),
    }
}

// ── Search handler ────────────────────────────────────────────────────────────

async fn handle_search(client: ExaClient, input: Input) {
    let Some(query) = input.query else {
        emit_err("'query' is required for action 'search'");
    };

    // Resolve contents options
    let contents = Some(resolve_contents(
        input.contents.as_ref(),
        input.max_chars,
        input.filter_empty_results,
        input.extras,
        input.max_age_hours,
    ));

    let opts = SearchOptions {
        query,
        num_results: input.num_results,
        search_type: input.search_type,
        category: input.category,
        include_domains: input.include_domains,
        exclude_domains: input.exclude_domains,
        start_crawl_date: input.start_crawl_date,
        end_crawl_date: input.end_crawl_date,
        start_published_date: input.start_published_date,
        end_published_date: input.end_published_date,
        include_text: input.include_text,
        exclude_text: input.exclude_text,
        use_autoprompt: input.use_autoprompt,
        moderation: input.moderation,
        user_location: input.user_location,
        additional_queries: input.additional_queries,
        contents,
    };

    if opts.num_results.unwrap_or(0) > 50 {
        emit_err("num_results exceeds maximum of 50");
    }

    match client.search(opts).await {
        Ok(resp) => {
            let formatted = format_results(&resp.results);
            emit_ok(&Output::SearchOk {
                ok: true,
                action: "search".to_string(),
                results: resp.results,
                resolved_search_type: resp.resolved_search_type,
                auto_date: resp.auto_date,
                search_time_ms: resp.search_time_ms,
                cost_dollars: resp.cost_dollars,
                formatted,
            });
        }
        Err(e) => emit_err(&format!("Search failed: {e}")),
    }
}

// ── FindSimilar handler ───────────────────────────────────────────────────────

async fn handle_find_similar(client: ExaClient, input: Input) {
    let Some(url) = input.url else {
        emit_err("'url' is required for action 'find_similar'");
    };

    let contents = Some(resolve_contents(
        input.contents.as_ref(),
        input.max_chars,
        input.filter_empty_results,
        input.extras,
        input.max_age_hours,
    ));

    let opts = FindSimilarOptions {
        url,
        num_results: input.num_results,
        include_domains: input.include_domains,
        exclude_domains: input.exclude_domains,
        start_crawl_date: input.start_crawl_date,
        end_crawl_date: input.end_crawl_date,
        start_published_date: input.start_published_date,
        end_published_date: input.end_published_date,
        include_text: input.include_text,
        exclude_text: input.exclude_text,
        exclude_source_domain: input.exclude_source_domain,
        category: input.category,
        contents,
    };

    if opts.num_results.unwrap_or(0) > 50 {
        emit_err("num_results exceeds maximum of 50");
    }

    match client.find_similar(opts).await {
        Ok(resp) => {
            let formatted = format_results(&resp.results);
            emit_ok(&Output::SearchOk {
                ok: true,
                action: "find_similar".to_string(),
                results: resp.results,
                resolved_search_type: None,
                auto_date: None,
                search_time_ms: None,
                cost_dollars: resp.cost_dollars,
                formatted,
            });
        }
        Err(e) => emit_err(&format!("FindSimilar failed: {e}")),
    }
}

// ── GetContents handler ───────────────────────────────────────────────────────

async fn handle_get_contents(client: ExaClient, input: Input) {
    let urls = match input.urls {
        Some(u) if !u.is_empty() => u,
        _ => emit_err("'urls' (non-empty array) is required for action 'get_contents'"),
    };

    // For get_contents, contents options are passed as top-level fields
    let resolved = input
        .contents
        .map(ContentsInput::into_options)
        .unwrap_or_default();

    // Apply legacy max_chars to text if not already set
    let text = resolved.text.or_else(|| {
        input.max_chars.map(|mc| TextOptions {
            max_characters: Some(mc),
            ..Default::default()
        })
    });

    let opts = GetContentsOptions {
        urls,
        text,
        summary: resolved.summary,
        highlights: resolved.highlights,
        livecrawl: resolved.livecrawl,
        livecrawl_timeout: resolved.livecrawl_timeout,
        max_age_hours: resolved.max_age_hours.or(input.max_age_hours),
        filter_empty_results: resolved.filter_empty_results.or(input.filter_empty_results),
        subpages: resolved.subpages,
        subpage_target: resolved.subpage_target,
        extras: resolved.extras.or(input.extras),
    };

    match client.get_contents(opts).await {
        Ok(resp) => {
            emit_ok(&Output::ContentsOk {
                ok: true,
                action: "get_contents".to_string(),
                results: resp.results,
                cost_dollars: resp.cost_dollars,
            });
        }
        Err(e) => emit_err(&format!("GetContents failed: {e}")),
    }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/// Resolve contents from protocol input + legacy `max_chars` and top-level shorthands.
/// If neither is provided, defaults to text with `max_characters=10000`
/// (preserves backwards-compat with old behaviour).
fn resolve_contents(
    contents_input: Option<&ContentsInput>,
    max_chars: Option<u32>,
    filter_empty_results: Option<bool>,
    extras: Option<ExtrasOptions>,
    max_age_hours: Option<i32>,
) -> ContentsOptions {
    if let Some(ci) = contents_input {
        let mut opts = ci.clone().into_options();
        // Apply legacy max_chars if text is enabled with no max_characters set
        if let Some(mc) = max_chars {
            if let Some(ref mut text) = opts.text {
                if text.max_characters.is_none() {
                    text.max_characters = Some(mc);
                }
            }
        }
        // Apply top-level shorthands as fallbacks
        if opts.filter_empty_results.is_none() {
            opts.filter_empty_results = filter_empty_results;
        }
        if opts.extras.is_none() {
            opts.extras = extras;
        }
        if opts.max_age_hours.is_none() {
            opts.max_age_hours = max_age_hours;
        }
        opts
    } else {
        // Legacy default: always request text
        let max_characters = max_chars.or(Some(10_000));
        ContentsOptions {
            text: Some(TextOptions {
                max_characters,
                ..Default::default()
            }),
            filter_empty_results,
            extras,
            max_age_hours,
            ..Default::default()
        }
    }
}

/// Validates that a string matches UUID v4 format without a regex dependency.
/// Expected: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (8-4-4-4-12 lowercase hex, dashes at fixed positions)
fn is_valid_uuid(s: &str) -> bool {
    let b = s.as_bytes();
    if b.len() != 36 {
        return false;
    }
    // Dashes must be at positions 8, 13, 18, 23
    if b[8] != b'-' || b[13] != b'-' || b[18] != b'-' || b[23] != b'-' {
        return false;
    }
    // All other positions must be lowercase hex digits
    for (i, &ch) in b.iter().enumerate() {
        if i == 8 || i == 13 || i == 18 || i == 23 {
            continue;
        }
        if !ch.is_ascii_hexdigit() || ch.is_ascii_uppercase() {
            return false;
        }
    }
    true
}

fn emit_ok(output: &Output) {
    match serde_json::to_string(output) {
        Ok(s) => println!("{s}"),
        Err(e) => eprintln!("Fatal: failed to serialize output: {e}"),
    }
}

fn emit_err(msg: &str) -> ! {
    let output = Output::Err {
        ok: false,
        error: msg.to_string(),
    };
    match serde_json::to_string(&output) {
        Ok(s) => eprintln!("{s}"),
        Err(e) => eprintln!("{{\"ok\":false,\"error\":\"Fatal serialization error: {e}\"}}"),
    }
    std::process::exit(1)
}
