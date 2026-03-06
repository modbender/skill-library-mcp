# Aegis Licensing

## Dual License Model

Aegis is available under a **dual license**:

### 1. Open Source — GNU Affero General Public License v3.0 (AGPL-3.0)

The source code in this repository is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). This means:

- You are free to use, modify, and distribute this software.
- If you modify the software and make it available over a network (e.g., as a SaaS product, internal service, or hosted tool), you **must** release your complete source code under the same AGPL-3.0 license.
- Any derivative works must also be licensed under AGPL-3.0.
- Full license text: [LICENSE](./LICENSE)

The AGPL-3.0 is an [OSI-approved](https://opensource.org/licenses/AGPL-3.0) open-source license.

### 2. Commercial / Enterprise License

For organizations that cannot comply with AGPL-3.0 obligations — for example, companies that:

- Want to embed Aegis in proprietary products or services
- Need to use Aegis without disclosing their own source code
- Want to run the Aegis MCP Proxy or Dashboard as an internal service without AGPL obligations
- Require SLAs, priority support, or enterprise-specific features

A **commercial enterprise license** is available that removes all AGPL-3.0 requirements.

**What the enterprise license includes:**

| Feature | AGPL-3.0 (Free) | Enterprise License |
|---------|------------------|-------------------|
| CLI Scanner (`aegis scan`) | Yes | Yes |
| Lockfile Verification (`aegis verify`) | Yes | Yes |
| MCP Proxy (Runtime Guard) | Yes (AGPL) | Yes (proprietary use OK) |
| Enterprise Dashboard | Yes (AGPL) | Yes (proprietary use OK) |
| Audit Log Export / SIEM Integration | Yes (AGPL) | Yes (proprietary use OK) |
| Embed in proprietary products | No (must release source) | Yes |
| Run as internal service without source disclosure | No | Yes |
| Priority support & SLA | No | Yes |
| Indemnification | No | Available |

**Contact:** For enterprise licensing inquiries, please contact [enterprise@aegis.network](mailto:enterprise@aegis.network).

## Contributing

By contributing to this project, you agree to the [Contributor License Agreement (CLA)](./CLA.md), which grants the project maintainers the right to distribute your contributions under both the AGPL-3.0 and the commercial enterprise license. This is necessary to maintain the dual-license model.

## FAQ

**Q: Can I use the free AGPL version for my company's internal tools?**
A: Yes, but if you modify Aegis and deploy it as a network service accessible to your users (even internal users), you must make the complete source code of your modified version available under AGPL-3.0.

**Q: Do I need the enterprise license just to run `aegis scan` in my CI pipeline?**
A: No. Running the unmodified CLI scanner in CI is fine under AGPL-3.0. The enterprise license is primarily for organizations that want to embed Aegis into proprietary services, run a modified proxy, or need commercial terms.

**Q: What if I use the AGPL version and later want to switch to enterprise?**
A: Contact us. We offer seamless transitions from AGPL to enterprise licensing.

**Q: Can cloud providers offer Aegis as a managed service under AGPL?**
A: Technically yes, but they must release the complete source code of their service (including any modifications and integration code) under AGPL-3.0. Most providers prefer the enterprise license instead.
