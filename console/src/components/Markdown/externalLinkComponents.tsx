/**
 * Shared react-markdown renderer overrides.
 *
 * [hanbao modification] Desktop shells (Tauri / pywebview) removed. The
 * default markdown <a> becomes a native anchor; this renderer intercepts the
 * click and hands the URL to `openExternalLink`, which opens it in a new tab
 * with scheme validation.
 */
import type { ComponentPropsWithoutRef } from "react";
import { openExternalLink } from "@/utils/openExternalLink";

// react-markdown injects an AST `node` prop alongside the standard anchor
// attributes; it must be kept off the rendered DOM element.
type AnchorProps = ComponentPropsWithoutRef<"a"> & { node?: unknown };

/** Markdown <a> renderer that opens links externally instead of navigating. */
export function ExternalMarkdownLink({
  node,
  href,
  children,
  ...rest
}: AnchorProps) {
  void node;
  return (
    <a
      {...rest}
      href={href}
      onClick={(event) => {
        event.preventDefault();
        if (href) openExternalLink(href);
      }}
      style={{ cursor: "pointer", ...rest.style }}
    >
      {children}
    </a>
  );
}

/** Drop-in `components` value for <ReactMarkdown> that safely opens links. */
export const externalLinkMarkdownComponents = {
  a: ExternalMarkdownLink,
};
