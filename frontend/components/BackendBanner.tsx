"use client";

import { getApiBaseCandidates } from "@/lib/api_base";
import { useEffect, useState } from "react";

export function BackendBanner() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const first = getApiBaseCandidates()[0] || "";
    const isLocal =
      first.includes("localhost") || first.includes("127.0.0.1") || first.includes("backend:8000");
    const isRemote = !window.location.hostname.match(/^localhost$|^127\.0\.0\.1$/);
    setShow(isLocal && isRemote);
  }, []);

  if (!show) return null;

  return (
    <div
      className="backend-banner"
      role="alert"
      style={{
        padding: "0.75rem 1rem",
        background: "linear-gradient(90deg, #fef3c7 0%, #fde68a 100%)",
        border: "1px solid #f59e0b",
        borderRadius: "12px",
        marginBottom: "1rem",
        fontSize: "0.9rem",
        color: "#92400e",
      }}
    >
      <strong>Backend bağlı değil.</strong> Bu adres (Vercel) sadece arayüzü sunar. Giriş ve veri
      için backend&apos;i yayına alıp Vercel ortam değişkenine{" "}
      <code style={{ background: "rgba(0,0,0,0.06)", padding: "0.1em 0.4em", borderRadius: "4px" }}>
        NEXT_PUBLIC_API_BASE_URL
      </code>{" "}
      ekleyin. Detay: <code>frontend/VERCEL.md</code>
    </div>
  );
}
