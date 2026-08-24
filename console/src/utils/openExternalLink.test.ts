// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  downloadFileFromUrl,
} from "./downloadFileFromUrl";
import { openExternalLink } from "./openExternalLink";

describe("openExternalLink", () => {
  const windowOpen = vi.fn();
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:download"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
    windowOpen.mockReset();
    vi.spyOn(window, "open").mockImplementation(windowOpen);
    localStorage.clear();
    (globalThis as any).VITE_API_BASE_URL = "";
    (globalThis as any).TOKEN = "";
    window.history.replaceState(null, "", "/");
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("ignores unsafe or fragment-only links", () => {
    openExternalLink("javascript:alert(1)");
    openExternalLink("#");

    expect(windowOpen).not.toHaveBeenCalled();
  });

  it("rejects ambiguous HTTP links without slashes before opening", () => {
    openExternalLink("http:example.com");

    expect(windowOpen).not.toHaveBeenCalled();
  });

  it("opens https links in a new tab via window.open", () => {
    openExternalLink("https://github.com/agentscope-ai/QwenPaw");

    expect(windowOpen).toHaveBeenCalledWith(
      "https://github.com/agentscope-ai/QwenPaw",
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("opens mailto links in a new tab via window.open", () => {
    openExternalLink("mailto:support@example.com");

    expect(windowOpen).toHaveBeenCalledWith(
      "mailto:support@example.com",
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("does not add auth query parameters to generic external links", () => {
    localStorage.setItem("hanbao_auth_token", "tok");

    openExternalLink("https://evil.example/api/foo");

    expect(windowOpen).toHaveBeenCalledWith(
      "https://evil.example/api/foo",
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("resolves relative links against the current origin before opening", () => {
    window.history.replaceState(null, "", "/console/inbox");

    openExternalLink("/docs/faq");

    expect(windowOpen).toHaveBeenCalledWith(
      "http://localhost:3000/docs/faq",
      "_blank",
      "noopener,noreferrer",
    );
  });

  it("rejects non-HTTP URLs before downloading", async () => {
    await expect(
      downloadFileFromUrl("mailto:support@example.com", "mail.zip"),
    ).rejects.toThrow("Download URL is invalid");

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects ambiguous HTTP downloads without slashes", async () => {
    await expect(
      downloadFileFromUrl("http:example.com/export.zip", "backup.zip"),
    ).rejects.toThrow("Download URL is invalid");

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("does not add auth query parameters to external API-shaped downloads", async () => {
    localStorage.setItem("hanbao_auth_token", "tok");
    fetchMock.mockResolvedValue(new Response("zip"));

    await expect(
      downloadFileFromUrl("https://evil.example/api/export", "backup.zip", {
        headers: { "X-Agent-Id": "agent-a" },
      }),
    ).resolves.toBeUndefined();

    expect(fetchMock).toHaveBeenCalledWith("https://evil.example/api/export", {
      headers: { "X-Agent-Id": "agent-a" },
    });
  });

  it("downloads via browser blob + anchor click", async () => {
    fetchMock.mockResolvedValue(
      new Response("zip", {
        headers: {
          "Content-Disposition": "attachment; filename*=UTF-8''server.zip",
        },
      }),
    );
    const click = vi.fn();
    const createElement = vi.spyOn(document, "createElement");
    createElement.mockImplementation((tagName: string) => {
      const element = document.createElementNS(
        "http://www.w3.org/1999/xhtml",
        tagName,
      ) as HTMLElement;
      if (tagName === "a") {
        element.click = click;
      }
      return element;
    });

    await expect(
      downloadFileFromUrl("/api/backups/abc/export", "backup.zip", {
        preferResponseFilename: true,
      }),
    ).resolves.toBeUndefined();

    expect(click).toHaveBeenCalled();
    expect(URL.revokeObjectURL).not.toHaveBeenCalledWith("blob:download");
    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:download");
  });
});
