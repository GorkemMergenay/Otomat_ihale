"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { clearClientAuthToken } from "@/lib/auth";

const links = [
  { href: "/", label: "Genel Bakış" },
  { href: "/tenders", label: "İhale Listesi" },
  { href: "/sources", label: "Kaynaklar" },
  { href: "/keywords", label: "Kural Yönetimi" },
  { href: "/notifications", label: "Bildirimler" },
];

export function SidebarNav({ activeSources }: { activeSources?: number }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <nav>
      {links.map((link) => {
        const isActive =
          pathname === link.href ||
          (link.href !== "/" && pathname.startsWith(`${link.href}/`));
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`nav-link${isActive ? " nav-link-active" : ""}`}
          >
            {link.label}
          </Link>
        );
      })}
      <button
        className="nav-link nav-logout"
        type="button"
        onClick={() => {
          clearClientAuthToken();
          router.push("/login");
          router.refresh();
        }}
      >
        Çıkış Yap
      </button>
    </nav>
  );
}
