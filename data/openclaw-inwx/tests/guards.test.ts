import { assertToolAllowed, isWriteTool } from "../src/guards";

describe("guards", () => {
  it("blocks write tools in readOnly mode", () => {
    expect(() => assertToolAllowed({ username: "u", password: "p", readOnly: true }, "inwx_domain_register")).toThrow(
      "readOnly=true",
    );
  });

  it("allows read tools in readOnly mode", () => {
    expect(() => assertToolAllowed({ username: "u", password: "p", readOnly: true }, "inwx_domain_check")).not.toThrow();
  });

  it("enforces allowedOperations whitelist", () => {
    expect(() =>
      assertToolAllowed({ username: "u", password: "p", allowedOperations: ["inwx_domain_check"] }, "inwx_domain_list"),
    ).toThrow("allowedOperations");
  });

  it("classifies read and write tools", () => {
    expect(isWriteTool("inwx_domain_check")).toBe(false);
    expect(isWriteTool("inwx_dns_record_add")).toBe(true);
  });
});
