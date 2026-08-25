/**
 * AsyncSyntaxHighlighter — [hanbao modification]
 *
 * 把 react-syntax-highlighter 包在动态 import 之后，使其巨大的 bundle
 * （Prism + refractor 全量语言，约 1MB+）只在真正渲染代码块时才下载，
 * 而不是被静态打进首屏 vendor chunk。chunk 加载完成前回退到纯 <pre>。
 *
 * 本文件为 hanbao 原创封装，受 Apache-2.0 约束；上游 QwenPaw v2.0.1 同类
 * 代码块渲染逻辑经减法式二次开发而来。
 * Copyright 2026 hanbao contributors
 */
import React, { useEffect, useState, type CSSProperties, type ReactNode } from "react";

interface HighlighterProps {
  language?: string;
  style?: CSSProperties;
  customStyle?: CSSProperties;
  wrapLongLines?: boolean;
  children: ReactNode;
}

export const AsyncSyntaxHighlighter: React.FC<HighlighterProps> = ({
  language,
  customStyle,
  wrapLongLines,
  children,
}) => {
  const [Highlighter, setHighlighter] =
    useState<React.ComponentType<HighlighterProps> | null>(null);
  const [style, setStyle] = useState<CSSProperties | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      import("react-syntax-highlighter"),
      import("react-syntax-highlighter/dist/esm/styles/prism"),
    ])
      .then(([mod, styles]) => {
        if (cancelled) return;
        setHighlighter(
          () =>
            mod.Prism as unknown as React.ComponentType<HighlighterProps>,
        );
        setStyle(styles.oneDark as CSSProperties);
      })
      .catch(() => {
        // 加载失败时保持 <pre> 回退，不影响其它内容渲染
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!Highlighter || !style) {
    return (
      <pre style={customStyle}>
        <code>{children}</code>
      </pre>
    );
  }

  return (
    <Highlighter
      language={language}
      style={style}
      customStyle={customStyle}
      wrapLongLines={wrapLongLines}
    >
      {children}
    </Highlighter>
  );
};

export default AsyncSyntaxHighlighter;
