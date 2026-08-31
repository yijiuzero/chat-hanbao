// [hanbao modification] Social links now point only to github.com/yijiuzero/chat-hanbao; all upstream AgentScope social channels (Discord/钉钉/小红书/微信/抖音/@agentscope_ai) removed. "Powered by" links retain §8 upstream attribution.
import { useState, type ReactNode, useRef } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { HanbaoMascot } from "@/components/HanbaoMascot";
import { GitHubIcon } from "./Icon";

const AGENTSCOPE_ORG = "https://github.com/agentscope-ai";
const AGENTSCOPE_REPO = "https://github.com/agentscope-ai/agentscope";
const AGENTSCOPE_RUNTIME =
  "https://github.com/agentscope-ai/agentscope-runtime";
const REME_REPO = "https://github.com/agentscope-ai/ReMe";

interface SocialLink {
  href: string;
  ariaLabel: string;
  icon: ReactNode;
  qrCode?: string;
}

interface PoweredByLink {
  href: string;
  labelKey: string;
}

const socialLinks: SocialLink[] = [
  {
    href: "https://github.com/yijiuzero/chat-hanbao",
    ariaLabel: "footer.social.github",
    icon: <GitHubIcon size={20} className="block text-orange-400" />,
  },
];

const poweredByLinks: PoweredByLink[] = [
  {
    href: AGENTSCOPE_ORG,
    labelKey: "footer.poweredBy.team",
  },
  {
    href: AGENTSCOPE_REPO,
    labelKey: "footer.poweredBy.agentscope",
  },
  {
    href: AGENTSCOPE_RUNTIME,
    labelKey: "footer.poweredBy.runtime",
  },
  {
    href: REME_REPO,
    labelKey: "footer.poweredBy.reme",
  },
];

export function Footer() {
  const { t } = useTranslation();
  const [hoveredLink, setHoveredLink] = useState<string | null>(null);
  const [qrPosition, setQrPosition] = useState({ top: 0, left: 0 });
  const linkRefs = useRef<Record<string, HTMLAnchorElement | null>>({});

  const linkClass =
    "block text-sm text-[var(--text-muted)] transition-colors hover:!text-(--color-primary)";
  const sectionTitleClass = "text-sm font-semibold text-[var(--text)]";

  const supportsHover = () => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return false;
    }
    return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  };

  const handleMouseEnter = (label: string) => {
    if (!supportsHover()) {
      return;
    }
    setHoveredLink(label);
    const element = linkRefs.current[label];
    if (element) {
      const rect = element.getBoundingClientRect();
      setQrPosition({
        top: rect.top - 180,
        left: rect.left + rect.width / 2,
      });
    }
  };

  const handleMouseLeave = () => {
    setHoveredLink(null);
  };

  const hoveredLinkData = socialLinks.find((l) => l.ariaLabel === hoveredLink);

  return (
    <footer className="mt-auto bg-white">
      <div className="mx-auto max-w-7xl px-6 py-10 md:py-12">
        <div className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between lg:gap-16">
          <section className="min-w-0 max-w-xl">
            <Link to="/" className="inline-flex items-center mb-4">
              <HanbaoMascot size={100} />
            </Link>
            <p className="mb-2 text-[15px] leading-7 text-(--text)">
              {t("whyHanbao.heroLine")}
              <br />
              {t("whyHanbao.secondPrefix")}
            </p>
            <div className="mt-5 flex items-center gap-4 text-[#f2a25b]">
              {socialLinks.map((link) => (
                <a
                  key={link.ariaLabel}
                  ref={(el) => {
                    if (el) {
                      linkRefs.current[link.ariaLabel] = el;
                    }
                  }}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={t(link.ariaLabel)}
                  className="relative inline-flex items-center justify-center w-6 h-6 leading-none"
                  onMouseEnter={() => handleMouseEnter(link.ariaLabel)}
                  onMouseLeave={handleMouseLeave}
                >
                  {link.icon}
                </a>
              ))}
            </div>
          </section>

          <section className="shrink-0 lg:ml-auto lg:text-right">
            <div className="space-y-3">
              <h4 className={sectionTitleClass}>
                {t("footer.sections.builtBy")}
              </h4>
              {poweredByLinks.map((link) => (
                <a
                  key={link.labelKey}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={linkClass}
                >
                  {t(link.labelKey)}
                </a>
              ))}
            </div>
          </section>
        </div>
      </div>

      {hoveredLink &&
        hoveredLinkData?.qrCode &&
        createPortal(
          <div
            className="fixed z-50 pointer-events-none"
            style={{
              top: `${qrPosition.top}px`,
              left: `${qrPosition.left}px`,
              transform: "translateX(-50%)",
            }}
            onMouseEnter={() => setHoveredLink(hoveredLink)}
            onMouseLeave={handleMouseLeave}
          >
            <div className="relative inline-block">
              {/* Content area */}
              <div className="rounded-lg border border-[#f0f0f0] bg-white p-3 shadow-[0_6px_16px_0_rgba(0,0,0,0.08),0_3px_6px_-4px_rgba(0,0,0,0.12),0_9px_28px_8px_rgba(0,0,0,0.05)]">
                <img
                  src={hoveredLinkData.qrCode}
                  alt=""
                  aria-hidden="true"
                  className="block w-35 h-35 rounded"
                />
              </div>
              {/* Bottom arrow */}
              <span
                aria-hidden="true"
                className="absolute left-1/2 top-full h-3 w-3 -translate-x-1/2 -translate-y-1/2 rotate-45 border-r border-b border-[#f0f0f0] bg-white"
              />
            </div>
          </div>,
          document.body,
        )}
    </footer>
  );
}
