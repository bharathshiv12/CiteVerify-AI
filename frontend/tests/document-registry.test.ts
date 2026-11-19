import { describe, it, expect, beforeEach } from "vitest";
import {
  registerDocument,
  getRegisteredDocuments,
  unregisterDocument,
} from "../lib/document-registry";

describe("Document Registry Deduplication & Local Persistence", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("stores and retrieves registered documents", () => {
    const doc = {
      document_id: "doc-1",
      filename: "test_paper.pdf",
      uploaded_at: "2026-11-19T10:00:00Z",
    };
    registerDocument(doc, "user-test");

    const retrieved = getRegisteredDocuments("user-test");
    expect(retrieved).toHaveLength(1);
    expect(retrieved[0].document_id).toBe("doc-1");
    expect(retrieved[0].filename).toBe("test_paper.pdf");
  });

  it("strictly deduplicates documents by document_id", () => {
    const doc1 = {
      document_id: "doc-unique",
      filename: "initial_name.pdf",
      uploaded_at: "2026-11-19T10:00:00Z",
    };
    const doc2 = {
      document_id: "doc-unique",
      filename: "updated_name.pdf",
      uploaded_at: "2026-11-19T10:05:00Z",
    };

    registerDocument(doc1, "user-test");
    registerDocument(doc2, "user-test");

    const retrieved = getRegisteredDocuments("user-test");
    expect(retrieved).toHaveLength(1);
    expect(retrieved[0].document_id).toBe("doc-unique");
    expect(retrieved[0].filename).toBe("updated_name.pdf");
  });

  it("unregisters a document cleanly without touching other records", () => {
    registerDocument({ document_id: "doc-a", filename: "a.pdf", uploaded_at: "2026-11-19" }, "user-test");
    registerDocument({ document_id: "doc-b", filename: "b.pdf", uploaded_at: "2026-11-19" }, "user-test");

    expect(getRegisteredDocuments("user-test")).toHaveLength(2);

    unregisterDocument("doc-a", "user-test");
    const remaining = getRegisteredDocuments("user-test");
    expect(remaining).toHaveLength(1);
    expect(remaining[0].document_id).toBe("doc-b");
  });
});
