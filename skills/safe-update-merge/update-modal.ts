// Source for: ui/src/ui/views/update-modal.ts
// Copy this to the OpenClaw repo after editing.

import { html, nothing } from "lit";

export type UpdateModalState = "closed" | "confirm" | "checking" | "result";

export interface UpdateModalModel {
  id: string;
  name?: string;
  provider: string;
}

export interface UpdateModalProps {
  state: UpdateModalState;
  divergence: { behind: number; ahead: number; upstreamRef: string; localRef: string; error?: string } | null;
  currentVersion: string;
  availableModels: UpdateModalModel[];
  selectedModel: string;
  onModelChange: (modelId: string) => void;
  onCheck: () => void;
  onRunMerge: () => void;
  onClose: () => void;
}

const STORAGE_KEY = "openclaw-merge-model";

export function getStoredMergeModel(): string {
  try { return localStorage.getItem(STORAGE_KEY) ?? ""; } catch { return ""; }
}

export function setStoredMergeModel(modelId: string): void {
  try { localStorage.setItem(STORAGE_KEY, modelId); } catch { /* noop */ }
}

/** Group models by provider for the <select> */
function renderModelOptions(models: UpdateModalModel[], selected: string) {
  const grouped = new Map<string, UpdateModalModel[]>();
  for (const m of models) {
    const list = grouped.get(m.provider) ?? [];
    list.push(m);
    grouped.set(m.provider, list);
  }

  const groups = [];
  for (const [provider, items] of [...grouped.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
    groups.push(html`
      <optgroup label=${provider}>
        ${items.map(m => html`
          <option value=${m.id} ?selected=${m.id === selected}>${m.name ?? m.id}</option>
        `)}
      </optgroup>
    `);
  }
  return groups;
}

export function renderUpdateModal(props: UpdateModalProps) {
  if (props.state === "closed") return nothing;

  const modelSelector = html`
    <div style="margin-top: 16px; text-align: left;">
      <label style="display: block; font-size: 12px; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">
        Merge Model
      </label>
      <select
        style="width: 100%; padding: 8px 10px; background: var(--bg-input, #111); color: var(--fg); border: 1px solid var(--border, #333); border-radius: 6px; font-size: 13px;"
        .value=${props.selectedModel}
        @change=${(e: Event) => {
          const val = (e.target as HTMLSelectElement).value;
          props.onModelChange(val);
        }}
      >
        <option value="">Agent default model</option>
        ${props.availableModels.length > 0
          ? renderModelOptions(props.availableModels, props.selectedModel)
          : nothing}
      </select>
      <div style="font-size: 11px; color: var(--muted); margin-top: 4px;">
        Model used for AI conflict resolution during merge
      </div>
    </div>
  `;

  return html`
    <div class="update-modal-overlay" @click=${(e: Event) => {
      if ((e.target as HTMLElement).classList.contains("update-modal-overlay")) {
        props.onClose();
      }
    }}>
      <div class="update-modal-panel">
        <div class="update-modal-header">
          <span style="font-size: 18px; font-weight: 600;">🔄 OpenClaw Update</span>
          <button class="btn small" @click=${props.onClose}>✕</button>
        </div>
        <div class="update-modal-body">
          ${props.state === "confirm" ? html`
            <div style="text-align: center; padding: 20px 0;">
              <div style="font-size: 40px; margin-bottom: 16px;">📡</div>
              <div style="font-size: 15px; color: var(--fg); margin-bottom: 8px;">
                Running <strong>v${props.currentVersion}</strong>
              </div>
              <div style="color: var(--muted); margin-bottom: 24px;">
                Check the upstream repository for new commits?
              </div>
              ${modelSelector}
              <button class="btn" style="margin-top: 20px; background: var(--accent); color: var(--bg); font-weight: 600; padding: 10px 28px; font-size: 14px;" @click=${props.onCheck}>
                Check for Updates
              </button>
            </div>
          ` : props.state === "checking" ? html`
            <div style="text-align: center; padding: 30px 0;">
              <div style="font-size: 40px; margin-bottom: 16px; animation: spin 1s linear infinite;">⏳</div>
              <div style="color: var(--muted);">Fetching from upstream…</div>
            </div>
          ` : props.state === "result" && props.divergence ? html`
            <div style="padding: 16px 0;">
              ${props.divergence.error ? html`
                <div style="text-align: center; padding: 10px 0;">
                  <div style="font-size: 40px; margin-bottom: 12px;">⚠️</div>
                  <div style="color: var(--danger, #ef4444); margin-bottom: 16px;">${props.divergence.error}</div>
                </div>
              ` : props.divergence.behind > 0 ? html`
                <div style="text-align: center;">
                  <div style="font-size: 40px; margin-bottom: 12px;">📦</div>
                  <div style="font-size: 15px; font-weight: 600; color: var(--accent); margin-bottom: 8px;">
                    ${props.divergence.behind} new commit${props.divergence.behind === 1 ? "" : "s"} available
                  </div>
                  <div style="color: var(--muted); font-size: 13px; margin-bottom: 4px;">
                    ${props.divergence.ahead > 0 ? `You are ${props.divergence.ahead} commit${props.divergence.ahead === 1 ? "" : "s"} ahead, ${props.divergence.behind} behind` : `Behind ${props.divergence.upstreamRef}`}
                  </div>
                </div>
              ` : html`
                <div style="text-align: center;">
                  <div style="font-size: 40px; margin-bottom: 12px;">✅</div>
                  <div style="font-size: 15px; font-weight: 600; color: var(--success, #22c55e); margin-bottom: 8px;">
                    Up to date with upstream
                  </div>
                  ${props.divergence.ahead > 0 ? html`
                    <div style="color: var(--muted); font-size: 13px;">
                      ${props.divergence.ahead} local commit${props.divergence.ahead === 1 ? "" : "s"} ahead
                    </div>
                  ` : nothing}
                </div>
              `}
              ${modelSelector}
              <div style="display: flex; gap: 10px; justify-content: center; margin-top: 24px;">
                <button class="btn" style="padding: 10px 20px;" @click=${props.onClose}>Close</button>
                <button class="btn" style="background: var(--accent); color: var(--bg); font-weight: 600; padding: 10px 20px;" @click=${props.onRunMerge}>
                  ${props.divergence.behind > 0 ? "⚡ Run Safe Merge" : "🔄 Run Merge Anyway"}
                </button>
              </div>
            </div>
          ` : nothing}
        </div>
      </div>
    </div>

    <style>
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      .update-modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.6);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(2px);
      }
      .update-modal-panel {
        background: var(--bg-card, #1a1a2e);
        border: 1px solid var(--border, #333);
        border-radius: 12px;
        width: 90vw;
        max-width: 440px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      }
      .update-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid var(--border, #333);
      }
      .update-modal-body {
        padding: 16px 20px;
      }
    </style>
  `;
}
