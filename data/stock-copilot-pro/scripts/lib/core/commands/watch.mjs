import { addWatchSymbol, loadWatchlist, removeWatchSymbol } from "../../config/watchlist.mjs";

export async function watchCommand(args = {}) {
  const action = String(args.watchAction || args.action || "list").toLowerCase();
  if (action === "list") {
    const state = await loadWatchlist();
    return {
      mode: "watch",
      action: "list",
      watchlist: state,
    };
  }

  const symbol = String(args.symbol || "").trim();
  if (!symbol) throw new Error("watch add/remove requires --symbol");
  const market = String(args.market || "GLOBAL").toUpperCase();
  const bucket = String(args.bucket || "watchlist").toLowerCase();

  if (action === "add") {
    const state = await addWatchSymbol(symbol, market, bucket);
    return { mode: "watch", action: "add", symbol, market, bucket, watchlist: state };
  }

  if (action === "remove") {
    const state = await removeWatchSymbol(symbol, market, bucket);
    return { mode: "watch", action: "remove", symbol, market, bucket, watchlist: state };
  }

  throw new Error(`Unknown watch action: ${action}`);
}
