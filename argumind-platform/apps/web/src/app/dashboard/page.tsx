"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { AppHeader } from "@/components/AppHeader";
import { UploadDocumentModal } from "@/components/UploadDocumentModal";
import { apiFetch, ArgumindApiError } from "@/lib/apiClient";

interface UserMe {
  readonly id: string;
  readonly full_name: string;
  readonly role: string;
}

interface DocumentRow {
  readonly id: string;
  readonly title: string;
  readonly domain_strata: string;
  readonly latest_version_number: number;
  readonly latest_version_id: string | null;
  readonly word_count: number;
  readonly status: string;
}

export default function DashboardPage(): React.JSX.Element {
  const router = useRouter();
  const [strataFilter, setStrataFilter] = useState<string>("");
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  const meQuery = useQuery({
    queryKey: ["auth-me"],
    queryFn: async () => {
      try {
        return await apiFetch<UserMe>("/api/v1/auth/me");
      } catch (err) {
        if (err instanceof ArgumindApiError && err.status === 401) {
          router.push("/login");
        }
        throw err;
      }
    },
  });

  const docsQuery = useQuery({
    queryKey: ["documents", strataFilter],
    enabled: Boolean(meQuery.data),
    queryFn: () => {
      const qs = strataFilter ? `?domain_strata=${strataFilter}` : "";
      return apiFetch<{ data: DocumentRow[]; meta: { total: number } }>(`/api/v1/documents${qs}`);
    },
  });

  const role = meQuery.data?.role ?? null;
  const docs = docsQuery.data?.data ?? [];

  return (
    <div className="min-h-screen">
      <AppHeader userRole={role} fullName={meQuery.data?.full_name ?? null} />
      <main className="mx-auto max-w-6xl p-4 md:p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">Daftar Dokumen Argumen</h1>
            <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
              Unggah draf analitis (300–2.500 kata) atau buka ruang anotasi riset.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              aria-label="Filter strata domain"
              value={strataFilter}
              onChange={(e) => setStrataFilter(e.target.value)}
              className="h-10 rounded-md border px-3 text-sm"
              style={{ borderColor: "var(--color-border)", backgroundColor: "var(--color-surface)" }}
            >
              <option value="">Semua Domain</option>
              <option value="academic">Esai Akademik</option>
              <option value="policy_business">Kebijakan & Bisnis</option>
            </select>
            {role !== "annotator" && (
              <button
                type="button"
                onClick={() => setIsUploadOpen(true)}
                className="h-10 rounded-md px-4 text-sm font-semibold text-white"
                style={{ backgroundColor: "var(--color-primary)" }}
              >
                + Dokumen Baru
              </button>
            )}
          </div>
        </div>

        <section className="mt-6 overflow-x-auto rounded-xl border" style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}>
          {docsQuery.isPending ? (
            <div className="flex flex-col gap-2 p-4" aria-busy="true">
              {[1, 2, 3].map((k) => (
                <div key={k} className="h-12 animate-pulse rounded" style={{ backgroundColor: "var(--color-surface-elevated)" }} />
              ))}
            </div>
          ) : docs.length === 0 ? (
            <div className="p-10 text-center">
              <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
                Belum ada dokumen tersedia di workspace ini.
              </p>
              {role !== "annotator" && (
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(true)}
                  className="mt-4 h-10 rounded-md px-4 text-sm font-semibold text-white"
                  style={{ backgroundColor: "var(--color-primary)" }}
                >
                  + Unggah Dokumen Pertama
                </button>
              )}
            </div>
          ) : (
            <table className="w-full text-left text-sm">
              <thead style={{ backgroundColor: "var(--color-surface-elevated)" }}>
                <tr className="h-10 border-b" style={{ borderColor: "var(--color-border)" }}>
                  <th className="px-4 font-semibold">Judul</th>
                  <th className="px-4 font-semibold">Strata</th>
                  <th className="px-4 font-semibold">Kata</th>
                  <th className="px-4 font-semibold">Status</th>
                  <th className="px-4 font-semibold">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((doc) => (
                  <tr key={doc.id} className="h-12 border-b" style={{ borderColor: "var(--color-border)" }}>
                    <td className="px-4 font-medium">{doc.title}</td>
                    <td className="px-4 font-mono text-xs">{doc.domain_strata}</td>
                    <td className="px-4 font-mono text-xs">{doc.word_count}</td>
                    <td className="px-4 font-mono text-xs">{doc.status}</td>
                    <td className="px-4">
                      <div className="flex flex-wrap gap-2">
                        {role !== "annotator" && (
                          <Link
                            href={`/documents/${doc.id}/versions/${doc.latest_version_number}/workspace`}
                            className="font-semibold underline"
                            style={{ color: "var(--color-primary)" }}
                          >
                            Ruang Kerja
                          </Link>
                        )}
                        {role === "annotator" && doc.latest_version_id && (
                          <Link
                            href={`/annotations/${doc.latest_version_id}`}
                            className="font-semibold underline"
                            style={{ color: "var(--color-secondary)" }}
                          >
                            Anotasi Blind
                          </Link>
                        )}
                        {(role === "reviewer" || role === "org_admin") && doc.latest_version_id && (
                          <Link
                            href={`/annotations/${doc.latest_version_id}/adjudicate`}
                            className="font-semibold underline"
                            style={{ color: "var(--color-secondary)" }}
                          >
                            Adjudikasi
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>

      <UploadDocumentModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onCreated={(docId) => {
          setIsUploadOpen(false);
          router.push(`/documents/${docId}/versions/1/workspace`);
        }}
      />
    </div>
  );
}
