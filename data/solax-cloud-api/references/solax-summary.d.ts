// SolaxSummary typing reference.
//
// IMPORTANT:
// - This is a best-effort interface. The exact fields depend on the `solax-cloud-api` package version
//   and the Solax Cloud API response.
// - When you run fetch_summary.mjs, the JSON it prints should conform to the SolaxSummary shape
//   exposed by the package you installed.
//
// If you want strict typing, we can generate this from the installed package types (if present)
// or from a sample response.

export interface SolaxSummary {
  // Common fields seen in Solax summary responses (may vary)
  sn?: string;
  plantName?: string;

  // Power / energy
  acPower?: number;
  yieldToday?: number;
  yieldTotal?: number;

  // Status
  inverterStatus?: string | number;

  // Allow additional fields
  [key: string]: unknown;
}
