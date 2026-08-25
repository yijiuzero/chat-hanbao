import type { ReactNode } from "react";
import type { ComponentProps } from "@ant-design/x-markdown";
import { MermaidCodeBlock } from "./MermaidCodeBlock";
// [hanbao modification] react-syntax-highlighter is loaded on demand via the
// AsyncSyntaxHighlighter wrapper so it stays out of the initial vendor chunk.
import { AsyncSyntaxHighlighter } from "@/components/AsyncSyntaxHighlighter";

/**
 * Extracts plain text from React children recursively.
 * XMarkdown may pass children as string or nested ReactNode elements.
 */
function extractText(children: ReactNode): string {
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(extractText).join("");
  if (children && typeof children === "object" && "props" in children) {
    return extractText(
      (children as { props: { children?: ReactNode } }).props.children,
    );
  }
  return "";
}

/**
 * Custom code component for XMarkdown that renders mermaid code blocks
 * as interactive diagrams, other code blocks with syntax highlighting,
 * and inline code as default.
 */
function CodeWithMermaid({
  children,
  lang,
  block,
  className,
  domNode: _domNode,
  streamStatus: _streamStatus,
  ...rest
}: ComponentProps) {
  if (block && lang === "mermaid") {
    const chartSource = extractText(children);
    if (chartSource.trim()) {
      return <MermaidCodeBlock chart={chartSource} />;
    }
  }

  if (block) {
    const codeText = extractText(children).replace(/\n$/, "");
    return (
      <AsyncSyntaxHighlighter
        language={lang || "text"}
        customStyle={{
          margin: 0,
          borderRadius: "6px",
          fontSize: "13px",
          lineHeight: "1.6",
        }}
      >
        {codeText}
      </AsyncSyntaxHighlighter>
    );
  }

  return (
    <code className={className} {...rest}>
      {children}
    </code>
  );
}

/**
 * XMarkdown components mapping that enables Mermaid diagram rendering.
 *
 * Usage:
 * ```tsx
 * <XMarkdown content={markdown} components={mermaidComponents} />
 * ```
 */
export const mermaidComponents: Record<
  string,
  React.ComponentType<ComponentProps>
> = {
  code: CodeWithMermaid,
};
