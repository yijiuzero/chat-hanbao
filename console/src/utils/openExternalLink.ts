/**
 * Open supported external links in a new browser tab.
 *
 * [hanbao modification] Desktop shells (Tauri / pywebview) removed — the
 * console is served as a plain web app, so every external link opens with the
 * browser's native `window.open`. URL scheme validation is kept so unsafe
 * links (e.g. `javascript:`, fragment-only) are still ignored.
 */
const URL_WITH_SCHEME_RE = /^[a-z][a-z\d+\-.]*:/i;
const HTTP_PROTOCOLS = new Set(["http:", "https:"]);
// Mailto / tel are opened by the OS handler via window.open.
const SUPPORTED_EXTERNAL_PROTOCOLS = new Set([
  "http:",
  "https:",
  "mailto:",
  "tel:",
]);

function hasHttpUrlPrefix(url: string): boolean {
  return /^https?:\/\//i.test(url);
}

/** Resolve absolute and app-relative URLs while ignoring empty or hash-only links. */
export function resolveExternalUrl(url: string): string | null {
  const trimmedUrl = url.trim();
  if (!trimmedUrl || trimmedUrl.startsWith("#")) {
    return null;
  }

  try {
    if (URL_WITH_SCHEME_RE.test(trimmedUrl)) {
      return trimmedUrl;
    }
    return new URL(trimmedUrl, window.location.origin).toString();
  } catch {
    return null;
  }
}

function protocolOf(url: string): string {
  return new URL(url).protocol;
}

/** Return true when a resolved URL is HTTP(S), the browser opener's scope. */
export function isHttpExternalUrl(url: string): boolean {
  try {
    return hasHttpUrlPrefix(url) && HTTP_PROTOCOLS.has(protocolOf(url));
  } catch {
    return false;
  }
}

function isSupportedExternalUrl(url: string): boolean {
  try {
    const protocol = protocolOf(url);
    if (HTTP_PROTOCOLS.has(protocol)) {
      return hasHttpUrlPrefix(url);
    }
    return SUPPORTED_EXTERNAL_PROTOCOLS.has(protocol);
  } catch {
    return false;
  }
}

/** Resolve an input URL only if its protocol is safe to hand to the opener. */
export function resolveSupportedExternalUrl(url: string): string | null {
  const resolvedUrl = resolveExternalUrl(url);
  if (!resolvedUrl || !isSupportedExternalUrl(resolvedUrl)) {
    return null;
  }

  return resolvedUrl;
}

/**
 * Open a supported external URL in a new browser tab.
 * Unsupported or unsafe URLs (e.g. `javascript:`, fragment-only) are ignored.
 */
export function openExternalLink(
  url: string,
  target: string = "_blank",
  features: string = "noopener,noreferrer",
): void {
  if (!url) return;

  const fullUrl = resolveSupportedExternalUrl(url);
  if (!fullUrl) {
    return;
  }

  window.open(fullUrl, target, features);
}
