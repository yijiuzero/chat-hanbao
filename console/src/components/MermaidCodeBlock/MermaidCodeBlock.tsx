import { useEffect, useState } from "react";
import styles from "./index.module.less";

/*
 * [hanbao modification] mermaid is dynamically imported inside the render
 * effect (see below) so its multi-MB core stays out of the initial vendor
 * chunk and only loads when a mermaid diagram is actually rendered.
 * Original source: QwenPaw v2.0.1 — licensed under Apache-2.0.
 */

let mermaidInitialized = false;
let idCounter = 0;

interface MermaidCodeBlockProps {
  chart: string;
}

export function MermaidCodeBlock({ chart }: MermaidCodeBlockProps) {
  const trimmedChart = chart.trim();
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [isRendering, setIsRendering] = useState<boolean>(!!trimmedChart);

  useEffect(() => {
    if (!trimmedChart) {
      setSvg("");
      setError("");
      setIsRendering(false);
      return;
    }

    let cancelled = false;
    const id = `mermaid-${Date.now()}-${idCounter++}`;
    setSvg("");
    setError("");
    setIsRendering(true);

    void (async () => {
      try {
        // [hanbao modification] dynamic import keeps mermaid out of the
        // initial vendor chunk; module caching guarantees a single init.
        const mermaidLib = (await import("mermaid")).default;
        if (!mermaidInitialized) {
          mermaidLib.initialize({
            startOnLoad: false,
            theme: "neutral",
            securityLevel: "loose",
          });
          mermaidInitialized = true;
        }
        const { svg: rendered } = await mermaidLib.render(id, trimmedChart);
        if (cancelled) return;
        setSvg(rendered);
        setError("");
        setIsRendering(false);
      } catch (renderError) {
        if (cancelled) return;
        setError(String(renderError));
        setSvg("");
        setIsRendering(false);
        const orphan = document.getElementById("d" + id);
        orphan?.remove();
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [trimmedChart]);

  if (error) {
    return (
      <pre className={styles.mermaidError}>
        <code>{chart}</code>
      </pre>
    );
  }

  return (
    <div
      className={`${styles.mermaidDiagram}${
        isRendering ? ` ${styles.isLoading}` : ""
      }`}
    >
      {isRendering ? (
        <div className={styles.placeholder} aria-hidden="true">
          Loading diagram…
        </div>
      ) : null}
      {svg ? (
        <div
          className={styles.content}
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      ) : null}
    </div>
  );
}
