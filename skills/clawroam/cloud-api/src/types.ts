export interface Vault {
  id: string;
  email: string;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
  created_at: Date;
}

export interface VaultKey {
  id: string;
  vault_id: string;
  public_key: string;
  fingerprint: string;
  hostname: string;
  instance_id: string;
  registered_at: Date;
  revoked_at: Date | null;
}

export interface VaultVersion {
  id: string;
  vault_id: string;
  s3_key: string;
  size_bytes: number;
  hash_sha256: string;
  pushed_by: string;
  created_at: Date;
}

export interface SignupRequest {
  email: string;
  public_key: string;
  hostname: string;
  os: string;
  instance_id: string;
}

export interface RegisterKeyRequest {
  public_key: string;
  hostname: string;
  instance_id: string;
}
