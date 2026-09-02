import { describe, expect, it } from "vitest";
import { commitDraftTag, consumeHashTags, mergeTags, normalizeTagName } from "@/lib/tag-input";

describe("tag input", () => {
  it("commits #tag followed by a space", () => {
    expect(consumeHashTags("#docker ")).toEqual({ tags: ["docker"], draft: "" });
    expect(consumeHashTags("keep #mcp #安全 ")).toEqual({ tags: ["mcp", "安全"], draft: "keep " });
  });

  it("accepts full-width hash and space", () => {
    expect(consumeHashTags("＃网络　")).toEqual({ tags: ["网络"], draft: "" });
  });

  it("does not commit until a space arrives", () => {
    expect(consumeHashTags("#draft")).toEqual({ tags: [], draft: "#draft" });
  });

  it("strips hashes when committing leftover draft", () => {
    expect(commitDraftTag("#Ops")).toBe("Ops");
    expect(normalizeTagName("  ＃已有  ")).toBe("已有");
  });

  it("merges tags without duplicates", () => {
    expect(mergeTags(["Docker"], ["Docker", "MCP"])).toEqual(["Docker", "MCP"]);
  });
});
