import { useTranslation } from "react-i18next";
import { LANGUAGES } from "../i18n";

export default function LanguageToggle() {
  const { i18n, t } = useTranslation();
  const current = i18n.language.startsWith("nl") ? "nl" : "en";
  return (
    <div
      role="group"
      aria-label={t("common.language")}
      className="inline-flex items-center rounded-full border border-stone-300 overflow-hidden text-xs"
    >
      {LANGUAGES.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => void i18n.changeLanguage(l)}
          aria-pressed={current === l}
          className={`px-2.5 py-1 font-semibold uppercase tracking-wider transition-colors ${
            current === l ? "bg-tuscan text-white" : "text-ink-2 hover:text-tuscan"
          }`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
