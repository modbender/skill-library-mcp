# Testing

## Dependencies

```toml
[dev-dependencies]
light-program-test = "0.19.0"
light-client = { version = "0.19.0", features = ["v2"] }
```

## Anchor Test

```rust
use light_program_test::{LightProgramTest, ProgramTestConfig, Rpc};
use light_sdk::interface::rent::SLOTS_PER_EPOCH;
use light_client::interface::{create_load_instructions, LightProgramInterface};

#[tokio::test]
async fn test_pool_lifecycle() {
    let config = ProgramTestConfig::new_v2(true, Some(vec![("my_amm", MY_AMM_ID)]));
    let mut rpc = LightProgramTest::new(config).await.unwrap();

    // 1. Init pool (rent-free)
    // ... build and send init instruction ...

    // 2. Swap (hot path - works normally)
    // ... build and send swap instruction ...

    // 3. Trigger compression (advance time)
    rpc.warp_slot_forward(SLOTS_PER_EPOCH * 30).await.unwrap();

    let pool_interface = rpc
        .get_account_interface(&pool_address, None)
        .await
        .unwrap()
        .value
        .unwrap();
    assert!(pool_interface.is_cold());

    // 4. Build SDK and get load instructions
    let sdk = AmmSdk::new(pool_address, pool_interface.data()).unwrap();
    let pubkeys = sdk.instruction_accounts(&AmmInstruction::Deposit);
    let accounts = rpc.get_multiple_account_interfaces(pubkeys.iter().collect(), None).await.unwrap().value;
    let cold: Vec<_> = accounts.into_iter().flatten().filter(|a| a.is_cold()).collect();

    let specs = sdk.load_specs(&cold).unwrap();
    let load_ixs = create_load_instructions(&specs, payer.pubkey(), config_pda, &rpc).await.unwrap();

    // 5. Send transaction
    rpc.create_and_send_transaction(&load_ixs, &payer.pubkey(), &[&payer]).await.unwrap();
}
```

| Resource | Link |
|----------|------|
| Test example | [program.rs](https://github.com/Lightprotocol/cp-swap-reference/blob/main/programs/cp-swap/tests/program.rs) |

## Pinocchio Test

```rust
use light_program_test::{LightProgramTest, Rpc};
use light_client::interface::{
    create_load_instructions, get_create_accounts_proof,
    AccountSpec, CreateAccountsProofInput, LightProgramInterface,
};


#[tokio::test]
async fn test_pool_lifecycle() {
    let mut rpc = LightProgramTest::new(config).await.unwrap();

    // 1. Initialize pool (rent-free: pool PDA, 2 mints, 2 vaults)
    let proof = get_create_accounts_proof(&rpc, &program_id, vec![
        CreateAccountsProofInput::pda(pool_state),
        CreateAccountsProofInput::mint(mint_a_signer),
        CreateAccountsProofInput::mint(mint_b_signer),
    ]).await.unwrap();

    rpc.create_and_send_transaction(&[init_ix], &payer.pubkey(), &[&payer, &authority])
        .await.unwrap();

    // 2. Swap (hot path)
    rpc.create_and_send_transaction(&[swap_ix], &user.pubkey(), &[&user])
        .await.unwrap();

    // 3. Trigger compression for the purpose of the test.
    const SLOTS_PER_EPOCH: u64 = 13500;
    rpc.warp_slot_forward(SLOTS_PER_EPOCH * 30).await.unwrap();

    // 4. Build SDK from pool state, fetch cold accounts
    let pool_iface = rpc.get_account_interface(&pool_state, None).await.unwrap().value.unwrap();
    assert!(pool_iface.is_cold());

    let sdk = SwapSdk::new(pool_state, pool_iface.data()).unwrap();
    let pubkeys = sdk.instruction_accounts(&SwapInstruction::Swap);
    let accounts = rpc.get_multiple_account_interfaces(pubkeys.iter().collect(), None)
        .await.unwrap().value;
    let cold: Vec<_> = accounts.into_iter().flatten().filter(|a| a.is_cold()).collect();

    // 5. Load cold accounts
    let mut specs = sdk.load_specs(&cold).unwrap();
    // Add user associated token accounts
    let ata_a = rpc.get_associated_token_account_interface(&user.pubkey(), &mint_a, None)
        .await.unwrap().value.unwrap();
    let ata_b = rpc.get_associated_token_account_interface(&user.pubkey(), &mint_b, None)
        .await.unwrap().value.unwrap();
    specs.push(AccountSpec::Ata(ata_a));
    specs.push(AccountSpec::Ata(ata_b));

    let load_ixs = create_load_instructions(&specs, payer.pubkey(), config_pda, &rpc)
        .await.unwrap();


    // 6. Load and Swap
    let mut all_ixs = load_ixs;
    all_ixs.push(swap_ix);
    rpc.create_and_send_transaction(&all_ixs, &user.pubkey(), &[&user])
        .await.unwrap();
}
```

| Resource | Link |
|----------|------|
| Full test | [test_lifecycle.rs](https://github.com/Lightprotocol/examples-light-token/blob/main/pinocchio/swap/tests/test_lifecycle.rs) |