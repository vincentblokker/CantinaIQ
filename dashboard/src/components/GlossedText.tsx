import { useMemo, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import * as Tooltip from "@radix-ui/react-tooltip";
import { GLOSSARY } from "../i18n/glossary";

function Glossed({ term, children }: { term: string; children: ReactNode }) {
  const entry = GLOSSARY[term.toLowerCase()];
  if (!entry) return <>{children}</>;
  return (
    <Tooltip.Root>
      <Tooltip.Trigger asChild>
        <span
          tabIndex={0}
          className="underline decoration-dotted decoration-tuscan/60 underline-offset-2 cursor-help"
        >
          {children}
        </span>
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content
          side="top"
          sideOffset={6}
          className="max-w-xs rounded-md bg-ink text-cream text-xs leading-snug px-3 py-2 shadow-lg z-50"
        >
          {entry.nl}
          <Tooltip.Arrow className="fill-ink" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}

/** Explicitly gloss an inline term (NL mode only). Useful where auto-wrap is
 *  undesirable or the term is embedded in formatted JSX. */
export function Term({ term, children }: { term: string; children?: ReactNode }) {
  const { i18n } = useTranslation();
  if (!i18n.language.startsWith("nl")) return <>{children ?? term}</>;
  return <Glossed term={term}>{children ?? term}</Glossed>;
}

// Escape a string for safe inclusion in a RegExp.
function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** Render a plain string; in NL mode, wrap the first occurrence of each known
 *  glossary term (whole-word, case-insensitive) in a tooltip. In EN mode the
 *  string renders unchanged. */
export default function GlossedText({ children }: { children: string }) {
  const { i18n } = useTranslation();
  const nl = i18n.language.startsWith("nl");

  const nodes = useMemo<ReactNode[]>(() => {
    if (!nl) return [children];
    const terms = Object.keys(GLOSSARY).sort((a, b) => b.length - a.length);
    const escaped = terms.map(escapeRegExp);
    // Letter-boundary lookarounds avoid matching inside larger words
    // (e.g. "doc" inside "document", "recall" inside "recalled"). More reliable
    // than \b here because terms contain hyphens, spaces and the "τ" character.
    const re = new RegExp(`(?<![A-Za-z])(${escaped.join("|")})(?![A-Za-z])`, "gi");
    const seen = new Set<string>();
    const out: ReactNode[] = [];
    let last = 0;
    let key = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(children)) !== null) {
      const matched = m[0];
      const lower = matched.toLowerCase();
      if (seen.has(lower)) continue; // first occurrence per term only
      seen.add(lower);
      if (m.index > last) out.push(children.slice(last, m.index));
      out.push(
        <Glossed key={key++} term={matched}>
          {matched}
        </Glossed>,
      );
      last = m.index + matched.length;
    }
    if (last < children.length) out.push(children.slice(last));
    return out;
  }, [children, nl]);

  return <>{nodes}</>;
}
