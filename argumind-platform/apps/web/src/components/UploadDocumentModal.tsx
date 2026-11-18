"use client";

import { useState } from "react";

import { apiFetch, ArgumindApiError } from "@/lib/apiClient";
import { useWorkspaceStore } from "@/stores/workspaceStore";

export interface UploadDocumentModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onCreated: (docId: string) => void;
}

export function UploadDocumentModal({
  isOpen,
  onClose,
  onCreated,
}: UploadDocumentModalProps): React.JSX.Element | null {
  const pushToast = useWorkspaceStore((s) => s.pushErrorToast);
  const [title, setTitle] = useState("");
  const [domainStrata, setDomainStrata] = useState<"academic" | "policy_business">("academic");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [researchOptIn, setResearchOptIn] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const isTextCountValid = file !== null || (words >= 300 && words <= 2500);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const form = new FormData();
      form.append("title", title);
      form.append("domain_strata", domainStrata);
      form.append("research_opt_in", String(researchOptIn));
      if (file) {
        form.append("file", file);
      } else {
        form.append("text", text);
      }
      const created = await apiFetch<{ document: { id: string } }>("/api/v1/documents", {
        method: "POST",
        body: form,
      });
      await apiFetch(`/api/v1/documents/${created.document.id}/versions/1/analyze`, {
        method: "POST",
        body: JSON.stringify({ generate_counterarguments: true }),
      });
      onCreated(created.document.id);
    } catch (err) {
      if (err instanceof ArgumindApiError) {
        pushToast({ code: err.code, detail: err.message, traceId: err.traceId });
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="upload-modal-title"
      className="fixed inset-0 z-40 flex items-center justify-center p-4"
      style={{ backgroundColor: "rgba(15, 23, 42, 0.60)" }}
    >
      <form
        onSubmit={(e) => void handleSubmit(e)}
        className="w-full max-w-[680px] rounded-xl p-6 shadow-lg"
        style={{ backgroundColor: "var(--color-surface)" }}
      >
        <h2 id="upload-modal-title" className="text-lg font-semibold">
          Unggah Dokumen Baru (F-01)
        </h2>

        <div className="mt-4 flex flex-col gap-3">
          <label className="text-sm font-medium">
            Judul Dokumen
            <input
              required
              minLength={2}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 h-10 w-full rounded-md border px-3 text-sm"
              style={{ borderColor: "var(--color-border)" }}
            />
          </label>

          <label className="text-sm font-medium">
            Strata Domain
            <select
              value={domainStrata}
              onChange={(e) => setDomainStrata(e.target.value as "academic" | "policy_business")}
              className="mt-1 h-10 w-full rounded-md border px-3 text-sm"
              style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface)" }}
            >
              <option value="academic">Esai Akademik Mahasiswa</option>
              <option value="policy_business">Kajian Kebijakan & Analisis Bisnis</option>
            </select>
          </label>

          <label className="text-sm font-medium">
            Unggah Berkas (.txt, .md, .docx, .pdf)
            <input
              type="file"
              accept=".txt,.md,.docx,.pdf"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="mt-1 block w-full text-sm"
            />
          </label>

          {!file && (
            <div>
              <div className="flex justify-between text-xs font-medium">
                <span>Atau Tempel Teks Bahasa Indonesia (300–2.500 kata)</span>
                <span style={{ color: isTextCountValid ? "var(--color-success)" : "var(--color-error)" }}>
                  {words} / 300–2500 kata
                </span>
              </div>
              <textarea
                rows={7}
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="mt-1 w-full rounded-md border p-3 text-sm"
                style={{ borderColor: "var(--color-border)" }}
              />
            </div>
          )}

          <label className="flex items-start gap-2 text-xs">
            <input
              type="checkbox"
              checked={researchOptIn}
              onChange={(e) => setResearchOptIn(e.target.checked)}
              className="mt-0.5 h-4 w-4"
            />
            <span>
              Saya menyetujui teks bersih (setelah redaksi identitas pribadi otomatis) dimasukkan ke korpus penelitian ilmiah Argumind.
            </span>
          </label>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            disabled={isSubmitting}
            onClick={onClose}
            className="h-10 rounded-md border px-4 text-sm"
            style={{ borderColor: "var(--color-border)" }}
          >
            Batal
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !isTextCountValid || title.trim().length < 2}
            className="h-10 rounded-md px-5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
            style={{ backgroundColor: "var(--color-primary)" }}
          >
            {isSubmitting ? "Memproses..." : "Analisis Argumen"}
          </button>
        </div>
      </form>
    </div>
  );
}
