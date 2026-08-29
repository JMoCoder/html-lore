"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { isDarkTheme, THEME_CHANGE_EVENT, toggleTheme } from "@/components/ui/theme";
import { useI18n } from "@/i18n/locale-provider";

export function ThemeToggle() {
  const { messages: t } = useI18n();
  const [dark, setDark] = useState(false);

  useEffect(() => {
    function sync() {
      setDark(isDarkTheme());
    }
    sync();
    window.addEventListener(THEME_CHANGE_EVENT, sync);
    return () => window.removeEventListener(THEME_CHANGE_EVENT, sync);
  }, []);

  return (
    <IconButton
      label={dark ? t.theme.toLight : t.theme.toDark}
      onClick={() => {
        toggleTheme();
        setDark(isDarkTheme());
      }}
    >
      <Icon.moon />
    </IconButton>
  );
}
