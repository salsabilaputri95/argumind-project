import type { Metadata } from "next";
import type { ReactNode } from "react";

import { Providers } from "@/components/Providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Argumind Platform — Evaluasi Struktur Argumen & Penalaran Kritis",
  description:
    "Platform pemetaan graf klaim-premis-bukti, deteksi premis implisit, dan rubrik terjelaskan.",
};

export default function RootLayout({
  children,
}: {
  readonly children: ReactNode;
}): React.JSX.Element {
  return (
    <html lang="id">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
