export const THEME_CHANGE_EVENT = "html-lore-theme";

export function ThemeScript() {
  const code = `try{if(localStorage.getItem('html-lore-theme')==='dark')document.documentElement.classList.add('dark')}catch(e){}`;
  return <script dangerouslySetInnerHTML={{ __html: code }} />;
}

export function isDarkTheme() {
  return document.documentElement.classList.contains("dark");
}

export function applyTheme(dark: boolean) {
  document.documentElement.classList.toggle("dark", dark);
  localStorage.setItem("html-lore-theme", dark ? "dark" : "light");
  window.dispatchEvent(new Event(THEME_CHANGE_EVENT));
}

export function toggleTheme() {
  applyTheme(!isDarkTheme());
}
