import { describe, it, expect } from "vitest";

function validatePdfFile(file: { name: string; type: string; size: number }, maxSizeMB = 25): { valid: boolean; error?: string } {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return { valid: false, error: "Invalid file format. Only academic PDF documents (.pdf) are accepted." };
  }
  if (file.type && file.type !== "application/pdf") {
    return { valid: false, error: "Invalid MIME type. Expected application/pdf." };
  }
  if (file.size === 0) {
    return { valid: false, error: "The selected file is empty (0 bytes). Please select a valid research document." };
  }
  const maxBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxBytes) {
    return { valid: false, error: `File size exceeds maximum limit of ${maxSizeMB}MB.` };
  }
  return { valid: true };
}

describe("PDF Upload Validation", () => {
  it("accepts valid PDF within size limit", () => {
    const file = { name: "quantum_transformers.pdf", type: "application/pdf", size: 2 * 1024 * 1024 };
    expect(validatePdfFile(file)).toEqual({ valid: true });
  });

  it("rejects non-PDF file extensions", () => {
    const file = { name: "paper.docx", type: "application/pdf", size: 1024 };
    const res = validatePdfFile(file);
    expect(res.valid).toBe(false);
    expect(res.error).toContain("Only academic PDF documents (.pdf) are accepted");
  });

  it("rejects invalid MIME types", () => {
    const file = { name: "paper.pdf", type: "image/png", size: 1024 };
    const res = validatePdfFile(file);
    expect(res.valid).toBe(false);
    expect(res.error).toContain("Invalid MIME type");
  });

  it("rejects 0-byte empty files", () => {
    const file = { name: "empty.pdf", type: "application/pdf", size: 0 };
    const res = validatePdfFile(file);
    expect(res.valid).toBe(false);
    expect(res.error).toContain("empty (0 bytes)");
  });

  it("rejects files exceeding max size limit", () => {
    const file = { name: "huge.pdf", type: "application/pdf", size: 30 * 1024 * 1024 };
    const res = validatePdfFile(file, 25);
    expect(res.valid).toBe(false);
    expect(res.error).toContain("exceeds maximum limit");
  });
});
