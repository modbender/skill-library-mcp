### 4. Audit Logging (Black Box)
*   **Trigger:** Before executing High-Risk commands (`rm`, `sudo`, `deploy`) or when an unrecoverable error occurs.
*   **Action:** Call `black-box --action log` to record your intent and status to the cloud.
