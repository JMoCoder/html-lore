export function ThemeScript() {
  const code = `try{if(localStorage.getItem('html-lore-theme')==='dark')document.documentElement.classList.add('dark')}catch(e){}`;
  return <script dangerouslySetInnerHTML={{ __html: code }} />;
}

export function toggleTheme() {
  const next = !document.documentElement.classList.contains("dark");
  document.documentElement.classList.toggle("dark", next);
  localStorage.setItem("html-lore-theme", next ? "dark" : "light");
}
