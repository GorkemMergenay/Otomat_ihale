import type { Metadata } from "next";
import { Manrope, Space_Mono, Sora } from "next/font/google";

import { BackendBanner } from "@/components/BackendBanner";
import { SidebarNav } from "@/components/SidebarNav";
import { getOverview } from "@/lib/api";
import "@/styles/globals.css";

const bodyFont = Manrope({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });
const monoFont = Space_Mono({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-space-mono",
});
const displayFont = Sora({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-sora" });

export const metadata: Metadata = {
  title: "Türkiye Otomat İhale Takip Sistemi",
  description: "Otomat, kiosk ve self servis ihale fırsatları için operasyon paneli",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  let overview: { active_sources: number } = { active_sources: 0 };
  try {
    overview = await getOverview();
  } catch {
    // API unavailable at build or first load
  }
  return (
    <html lang="tr">
      <body className={`${bodyFont.className} ${monoFont.variable} ${displayFont.variable}`}>
        <div className="page-bg" />
        <div className="shell">
          <aside className="sidebar">
            <div className="brand-block">
              <p className="brand-kicker">KAMU İHALE RADARI</p>
              <h1>Türkiye Otomat Takip</h1>
              <p>
                Resmi kaynak doğrulaması, açıklanabilir skor ve operasyon aksiyonları tek ekranda.
              </p>
            </div>
            <SidebarNav activeSources={overview.active_sources} />
            <div className="sidebar-foot">
              <p>Aktif kaynak</p>
              <strong>{overview.active_sources} kaynak</strong>
            </div>
          </aside>
          <main className="content">
            <BackendBanner />
            <div className="content-top" aria-hidden>
              Canlı panel
            </div>
            <div className="content-inner">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
