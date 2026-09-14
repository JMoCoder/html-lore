import { describe, expect, it } from "vitest";
import { uniqueTitle } from "@/server/unique-title";

describe("uniqueTitle", () => {
  it("keeps the original title when free", () => {
    expect(uniqueTitle("Bank note", ["Other"])).toBe("Bank note");
  });

  it("appends a numeric suffix when the title collides", () => {
    expect(uniqueTitle("Bank note", ["Bank note"])).toBe("Bank note 2");
    expect(uniqueTitle("Bank note", ["Bank note", "Bank note 2"])).toBe("Bank note 3");
  });

  it("treats collisions as case-insensitive", () => {
    expect(uniqueTitle("Bank Note", ["bank note"])).toBe("Bank Note 2");
  });

  it("falls back to Untitled when blank", () => {
    expect(uniqueTitle("  ", [])).toBe("Untitled");
    expect(uniqueTitle("", ["Untitled"])).toBe("Untitled 2");
  });
});
