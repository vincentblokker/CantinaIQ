import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { en } from "./locales/en";
import { nl } from "./locales/nl";

export const LANGUAGES = ["en", "nl"] as const;
export type Language = (typeof LANGUAGES)[number];

const STORAGE_KEY = "cantinaiq.lang";

function initialLanguage(): Language {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "nl" || stored === "en" ? stored : "en";
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, nl: { translation: nl } },
  lng: initialLanguage(),
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

i18n.on("languageChanged", (lng) => {
  localStorage.setItem(STORAGE_KEY, lng);
  document.documentElement.lang = lng;
});
document.documentElement.lang = i18n.language;

export default i18n;
