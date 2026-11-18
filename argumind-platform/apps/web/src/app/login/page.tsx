"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiFetch, ArgumindApiError } from "@/lib/apiClient";
import { useWorkspaceStore } from "@/stores/workspaceStore";

interface LoginResponse {
  readonly mfa_required: boolean;
  readonly mfa_challenge_token?: string;
}

export default function LoginPage(): React.JSX.Element {
  const router = useRouter();
  const pushToast = useWorkspaceStore((s) => s.pushErrorToast);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [challengeToken, setChallengeToken] = useState<string | null>(null);
  const [totpCode, setTotpCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleLogin(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await apiFetch<LoginResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (res.mfa_required && res.mfa_challenge_token) {
        setChallengeToken(res.mfa_challenge_token);
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      if (err instanceof ArgumindApiError) {
        pushToast({ code: err.code, detail: err.message, traceId: err.traceId });
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function handleMfa(e: React.FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    if (!challengeToken) return;
    setIsLoading(true);
    try {
      await apiFetch("/api/v1/auth/mfa/verify", {
        method: "POST",
        body: JSON.stringify({ mfa_challenge_token: challengeToken, totp_code: totpCode }),
      });
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ArgumindApiError) {
        pushToast({ code: err.code, detail: err.message, traceId: err.traceId });
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div
        className="w-full max-w-md rounded-xl border p-8 shadow-md"
        style={{ backgroundColor: "var(--color-surface)", borderColor: "var(--color-border)" }}
      >
        <h1 className="text-2xl font-bold" style={{ color: "var(--color-primary)" }}>
          Argumind
        </h1>
        <p className="mt-1 text-sm" style={{ color: "var(--color-text-secondary)" }}>
          Masuk untuk menganalisis struktur argumen & penalaran kritis.
        </p>

        {!challengeToken ? (
          <form onSubmit={(e) => void handleLogin(e)} className="mt-6 flex flex-col gap-4">
            <label className="text-sm font-medium">
              Email Institusi
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 h-10 w-full rounded-md border px-3 text-sm"
                style={{ borderColor: "var(--color-border)" }}
              />
            </label>
            <label className="text-sm font-medium">
              Kata Sandi
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 h-10 w-full rounded-md border px-3 text-sm"
                style={{ borderColor: "var(--color-border)" }}
              />
            </label>
            <button
              type="submit"
              disabled={isLoading}
              className="h-11 rounded-md text-sm font-semibold text-white"
              style={{ backgroundColor: "var(--color-primary)" }}
            >
              {isLoading ? "Memverifikasi..." : "Masuk"}
            </button>
          </form>
        ) : (
          <form onSubmit={(e) => void handleMfa(e)} className="mt-6 flex flex-col gap-4">
            <label className="text-sm font-medium">
              Kode MFA TOTP (6 Digit)
              <input
                type="text"
                inputMode="numeric"
                minLength={6}
                maxLength={6}
                required
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                className="mt-1 h-10 w-full rounded-md border px-3 font-mono text-sm tracking-widest"
                style={{ borderColor: "var(--color-border)" }}
              />
            </label>
            <button
              type="submit"
              disabled={isLoading}
              className="h-11 rounded-md text-sm font-semibold text-white"
              style={{ backgroundColor: "var(--color-primary)" }}
            >
              Verifikasi MFA
            </button>
          </form>
        )}

        <p className="mt-6 text-xs" style={{ color: "var(--color-text-secondary)" }}>
          Kebijakan Privasi: Pemrosesan LLM menerapkan zero data retention dan redaksi PII otomatis.
        </p>
      </div>
    </main>
  );
}
