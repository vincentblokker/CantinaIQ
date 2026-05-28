// Wikipedia page-summary fetch with Dutch-first resolution.
//
// The dashboard stores English article titles/slugs. In NL mode we resolve the
// Dutch article via Wikipedia's langlinks API and fetch its summary, falling
// back to the English summary when no Dutch article exists.
export interface WikiSummary {
  extract: string;
  thumbnail?: { source: string };
  content_urls?: { desktop?: { page: string } };
}

const restSummary = (lang: string, title: string) =>
  `https://${lang}.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;

// Resolve the Dutch article title for an English title via langlinks.
async function dutchTitleFor(enTitle: string): Promise<string | null> {
  const url =
    `https://en.wikipedia.org/w/api.php?action=query&prop=langlinks&lllang=nl` +
    `&lllimit=1&redirects=1&format=json&origin=*&titles=${encodeURIComponent(enTitle)}`;
  const r = await fetch(url);
  if (!r.ok) return null;
  const j = await r.json();
  const pages: Record<string, { langlinks?: { "*": string }[] }> =
    j?.query?.pages ?? {};
  for (const key of Object.keys(pages)) {
    const link = pages[key]?.langlinks?.[0]?.["*"];
    if (link) return link;
  }
  return null;
}

function isUsable(j: WikiSummary | null): j is WikiSummary {
  return (
    !!j &&
    typeof j.extract === "string" &&
    j.extract.length > 80 &&
    !/may refer to|kan verwijzen naar|doorverwijspagina/i.test(j.extract)
  );
}

async function summary(lang: string, title: string): Promise<WikiSummary | null> {
  try {
    const r = await fetch(restSummary(lang, title));
    if (!r.ok) return null;
    return (await r.json()) as WikiSummary;
  } catch {
    return null;
  }
}

/**
 * Fetch a usable page summary for the first matching candidate English title.
 * When `nl` is true, prefer the Dutch article (resolved via langlinks); fall
 * back to the English summary if no Dutch article exists or it isn't usable.
 */
export async function fetchWikiSummary(
  candidates: (string | null | undefined)[],
  nl: boolean,
): Promise<WikiSummary | null> {
  const titles = candidates.filter((c): c is string => !!c);
  // Dutch-first: try a Dutch article for every candidate before falling back,
  // so a candidate with a Dutch equivalent wins over an earlier English-only one.
  if (nl) {
    for (const enTitle of titles) {
      try {
        const nlTitle = await dutchTitleFor(enTitle);
        if (nlTitle) {
          const dutch = await summary("nl", nlTitle);
          if (isUsable(dutch)) return dutch;
        }
      } catch {
        // try next candidate
      }
    }
  }
  for (const enTitle of titles) {
    const english = await summary("en", enTitle);
    if (isUsable(english)) return english;
  }
  return null;
}
