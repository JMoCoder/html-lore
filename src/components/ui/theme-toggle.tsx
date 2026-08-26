"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  return (
    <IconButton
      label={dark ? "切换为亮色" : "切换为暗色"}
      onClick={() => {
        const next = !document.documentElement.classList.contains("dark");
        document.documentElement.classList.toggle("dark", next);
        localStorage.setItem("html-lore-theme", next ? "dark" : "light");
        setDark(next);
      }}
    >
      <Icon.moon />
    </IconButton>
  );
}
