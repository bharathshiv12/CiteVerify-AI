export interface RegisteredDocument {
  document_id: string;
  filename: string;
  uploaded_at: string;
  file_size_bytes?: number;
  total_claims?: number;
  verified_claims?: number;
  status?: string;
  pipeline_stage?: string;
}

function getStorageKey(userId?: string): string {
  return `citeverify_registry_${userId || "anonymous"}`;
}

export function getRegisteredDocuments(userId?: string): RegisteredDocument[] {
  if (typeof window === "undefined" || !window.localStorage) {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(getStorageKey(userId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function registerDocument(
  doc: RegisteredDocument,
  userId?: string
): RegisteredDocument[] {
  if (typeof window === "undefined" || !window.localStorage) {
    return [doc];
  }
  try {
    const existing = getRegisteredDocuments(userId);
    const filtered = existing.filter((item) => item.document_id !== doc.document_id);
    const updated = [doc, ...filtered];
    window.localStorage.setItem(getStorageKey(userId), JSON.stringify(updated));
    return updated;
  } catch {
    return [doc];
  }
}

export function unregisterDocument(
  documentId: string,
  userId?: string
): RegisteredDocument[] {
  if (typeof window === "undefined" || !window.localStorage) {
    return [];
  }
  try {
    const existing = getRegisteredDocuments(userId);
    const updated = existing.filter((item) => item.document_id !== documentId);
    window.localStorage.setItem(getStorageKey(userId), JSON.stringify(updated));
    return updated;
  } catch {
    return [];
  }
}
