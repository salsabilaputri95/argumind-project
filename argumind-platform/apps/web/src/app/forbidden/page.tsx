import Link from "next/link";

export default function ForbiddenPage(): React.JSX.Element {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 text-center">
      <div
        className="max-w-md rounded-xl border p-8 shadow-sm"
        style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}
      >
        <p className="font-mono text-sm font-bold" style={{ color: "var(--color-error)" }}>
          HTTP 403 • ERR_ROLE_FORBIDDEN
        </p>
        <h1 className="mt-2 text-2xl font-bold">Akses Ditolak</h1>
        <p className="mt-2 text-sm" style={{ color: "var(--color-text-secondary)" }}>
          Peran akun Anda tidak memiliki izin untuk membuka halaman ini atau melihat data anotasi blind rekan lain.
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-flex h-10 items-center rounded-md px-5 text-sm font-semibold text-white"
          style={{ backgroundColor: "var(--color-primary)" }}
        >
          Kembali ke Dashboard
        </Link>
      </div>
    </main>
  );
}
