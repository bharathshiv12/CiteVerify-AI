import { describe, it, expect } from "vitest";
import { ApiError } from "../services/api";

describe("API Error Envelope Parsing", () => {
  it("constructs an ApiError with code, details, request_id, and HTTP status", () => {
    const error = new ApiError(
      "The uploaded file does not contain valid PDF magic bytes.",
      400,
      "INVALID_PDF_MAGIC_BYTES",
      { detected_header: "47494638" },
      "8f2a1c90-9941-4c5b-9988-123456789abc"
    );

    expect(error.message).toBe("The uploaded file does not contain valid PDF magic bytes.");
    expect(error.status).toBe(400);
    expect(error.code).toBe("INVALID_PDF_MAGIC_BYTES");
    expect(error.details).toEqual({ detected_header: "47494638" });
    expect(error.request_id).toBe("8f2a1c90-9941-4c5b-9988-123456789abc");
  });

  it("handles fallback defaults gracefully when details or request_id are omitted", () => {
    const error = new ApiError("Internal error", 500);
    expect(error.status).toBe(500);
    expect(error.code).toBe("UNKNOWN_ERROR");
    expect(error.details).toBeUndefined();
    expect(error.request_id).toBeUndefined();
  });
});
