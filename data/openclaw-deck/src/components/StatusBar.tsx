import { useDeckStats } from "../hooks";
import { useDeckStore } from "../lib/store";
import styles from "./StatusBar.module.css";

export function StatusBar() {
  const stats = useDeckStats();
  const gatewayUrl = useDeckStore((s) => s.config.gatewayUrl);

  return (
    <div className={styles.bar}>
      <span>
        {gatewayUrl}{" "}
        <span
          className={
            stats.gatewayConnected ? styles.connected : styles.disconnected
          }
        >
          {stats.gatewayConnected ? "connected" : "disconnected"}
        </span>
      </span>
      <span className={styles.sep}>·</span>
      <span>
        {stats.totalAgents} agents · {stats.active} active
        {stats.errors > 0 && <> · <span className={styles.error}>{stats.errors} {stats.errors === 1 ? "error" : "errors"}</span></>}
      </span>
      <span className={styles.spacer} />
      <span>openclaw-deck v0.1.0</span>
    </div>
  );
}
