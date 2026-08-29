const RUNTIME = `
<style id="html-lore-visual-editor-style">
  [data-html-lore-selected="true"] { outline: 2px solid #2f7f68 !important; outline-offset: 2px !important; }
  [data-html-lore-hover="true"] { outline: 1px dashed rgba(47,127,104,.65) !important; outline-offset: 2px !important; }
  [data-html-lore-editing-text="true"] { cursor: text !important; }
</style>
<script id="html-lore-visual-editor-runtime">
(() => {
  const blocked = new Set(["HTML","BODY","HEAD","META","TITLE","STYLE","SCRIPT","LINK","IFRAME","OBJECT","EMBED","CANVAS","SVG","NOSCRIPT"]);
  const textTargets = new Set(["P","H1","H2","H3","H4","H5","H6","LI","A","BUTTON","SPAN","STRONG","EM","SMALL","LABEL","TD","TH","BLOCKQUOTE","PRE","CODE","FIGCAPTION"]);
  const inlineTargets = new Set(["A","BUTTON","SPAN","STRONG","EM","SMALL","LABEL","CODE","B","I","U","S","MARK"]);
  let selected = null;
  let hover = null;
  let mode = "text";
  function pathFor(element) {
    const parts = [];
    let node = element;
    while (node && node.nodeType === 1 && node !== document.documentElement) {
      const parent = node.parentElement;
      if (!parent) break;
      const index = Array.from(parent.children).indexOf(node);
      parts.unshift(index);
      node = parent;
    }
    return parts.join(".");
  }
  function elementFor(path) {
    if (!path) return null;
    let node = document.documentElement;
    for (const raw of path.split(".")) {
      const index = Number(raw);
      if (!Number.isInteger(index) || !node.children[index]) return null;
      node = node.children[index];
    }
    return node;
  }
  function editable(element) {
    if (!element || blocked.has(element.tagName)) return false;
    if (element.closest("script,style,iframe,object,embed,canvas,svg")) return false;
    return true;
  }
  function selectable(element) {
    if (!editable(element)) return false;
    if (textTargets.has(element.tagName)) return true;
    if (isCompositeTextBlock(element)) return true;
    if (element.children.length === 0 && (element.textContent || "").trim()) return true;
    return false;
  }
  function isCompositeTextBlock(element) {
    if (!editable(element) || !String(element.textContent || "").trim()) return false;
    if (element.children.length === 0 || element.children.length > 8) return false;
    const hasOwnText = Array.from(element.childNodes).some((node) => node.nodeType === Node.TEXT_NODE && String(node.textContent || "").trim());
    if (!hasOwnText) return false;
    return Array.from(element.children).every((child) => inlineTargets.has(child.tagName));
  }
  function selectionTarget(rawTarget) {
    let target = rawTarget;
    if (target && target.nodeType === Node.TEXT_NODE) target = target.parentElement;
    if (!target || target.nodeType !== Node.ELEMENT_NODE) return null;
    const parent = target.parentElement;
    if (inlineTargets.has(target.tagName) && isCompositeTextBlock(parent)) return parent;
    return target;
  }
  function snapshot(element) {
    const computed = getComputedStyle(element);
    return {
      path: pathFor(element),
      tag: element.tagName.toLowerCase(),
      text: element.textContent || "",
      style: {
        color: element.style.color || rgbToHex(computed.color, "#000000"),
        backgroundColor: element.style.backgroundColor || inheritedBackgroundColor(element),
        fontSize: parseFloat(computed.fontSize) || "",
        lineHeight: computed.lineHeight === "normal" ? "" : parseFloat(computed.lineHeight) / (parseFloat(computed.fontSize) || 16),
        fontWeight: element.style.fontWeight || computed.fontWeight || "",
        fontStyle: element.style.fontStyle || computed.fontStyle || "",
        textDecoration: element.style.textDecoration || computed.textDecorationLine || "",
        textAlign: element.style.textAlign || computed.textAlign || "",
      },
    };
  }
  function select(element) {
    if (!editable(element)) {
      parent.postMessage({ type: "html-lore-file-editor-unsupported" }, "*");
      return;
    }
    if (selected) {
      selected.removeAttribute("data-html-lore-selected");
      selected.removeAttribute("data-html-lore-editing-text");
      selected.removeAttribute("contenteditable");
    }
    selected = element;
    selected.setAttribute("data-html-lore-selected", "true");
    applyMode();
    parent.postMessage({ type: "html-lore-file-editor-select", selection: snapshot(element) }, "*");
  }
  function applyMode() {
    if (!selected) return;
    if (mode === "text") {
      selected.setAttribute("contenteditable", "plaintext-only");
      selected.setAttribute("data-html-lore-editing-text", "true");
      selected.focus({ preventScroll: true });
    } else {
      selected.removeAttribute("contenteditable");
      selected.removeAttribute("data-html-lore-editing-text");
    }
  }
  function rgbToHex(value, fallback) {
    const text = String(value || "");
    const match = text.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?/i);
    if (!match) return fallback;
    if (match[4] !== undefined && Number(match[4]) === 0) return fallback;
    return "#" + [match[1], match[2], match[3]].map((part) => Number(part).toString(16).padStart(2, "0")).join("");
  }
  function inheritedBackgroundColor(element) {
    let node = element;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
      const value = getComputedStyle(node).backgroundColor;
      const hex = rgbToHex(value, "");
      if (hex) return hex;
      node = node.parentElement;
    }
    return "#ffffff";
  }
  function serialize() {
    const clone = document.documentElement.cloneNode(true);
    clone.querySelector("#html-lore-visual-editor-style")?.remove();
    clone.querySelector("#html-lore-visual-editor-runtime")?.remove();
    clone.querySelectorAll("[data-html-lore-selected],[data-html-lore-hover]").forEach((node) => {
      node.removeAttribute("data-html-lore-selected");
      node.removeAttribute("data-html-lore-hover");
      node.removeAttribute("data-html-lore-editing-text");
      node.removeAttribute("contenteditable");
    });
    return "<!doctype html>\\n" + clone.outerHTML;
  }
  document.addEventListener("mouseover", (event) => {
    const target = selectionTarget(event.target);
    if (!selectable(target) || target === selected) return;
    if (hover) hover.removeAttribute("data-html-lore-hover");
    hover = target;
    hover.setAttribute("data-html-lore-hover", "true");
  }, true);
  document.addEventListener("mouseout", () => {
    if (hover) hover.removeAttribute("data-html-lore-hover");
    hover = null;
  }, true);
  document.addEventListener("click", (event) => {
    const target = selectionTarget(event.target);
    if (mode === "text" && target === selected) return;
    if (!selectable(target)) return;
    event.preventDefault();
    event.stopPropagation();
    select(target);
  }, true);
  document.addEventListener("input", (event) => {
    if (!selected || event.target !== selected) return;
    parent.postMessage({ type: "html-lore-file-editor-direct-text", selection: snapshot(selected) }, "*");
  }, true);
  window.addEventListener("message", (event) => {
    const message = event.data || {};
    if (message.type === "html-lore-file-editor-mode") {
      mode = message.mode === "element" ? "element" : "text";
      applyMode();
    }
    if (message.type === "html-lore-file-editor-apply") {
      const element = elementFor(message.path);
      if (!editable(element)) return;
      if ("text" in message.values) element.textContent = String(message.values.text || "");
      const style = message.values.style || {};
      for (const [key, value] of Object.entries(style)) {
        element.style[key] = value == null ? "" : String(value);
      }
      if (message.silent) return;
      select(element);
    }
    if (message.type === "html-lore-file-editor-select") {
      const element = elementFor(message.path);
      if (editable(element)) select(element);
    }
    if (message.type === "html-lore-file-editor-serialize") {
      parent.postMessage({ type: "html-lore-file-editor-serialized", html: serialize(), requestId: message.requestId }, "*");
    }
  });
})();
</script>`;

export function injectFileEditorRuntime(source: string) {
  if (/<\/body\s*>/i.test(source)) return source.replace(/<\/body\s*>/i, `${RUNTIME}</body>`);
  return `${source}${RUNTIME}`;
}

export function stripFileEditorRuntime(doc: Document) {
  const clone = doc.documentElement.cloneNode(true) as HTMLElement;
  clone.querySelector("#html-lore-visual-editor-style")?.remove();
  clone.querySelector("#html-lore-visual-editor-runtime")?.remove();
  clone.querySelectorAll("[data-html-lore-selected],[data-html-lore-hover],[data-html-lore-editing-text],[contenteditable]").forEach((node) => {
    node.removeAttribute("data-html-lore-selected");
    node.removeAttribute("data-html-lore-hover");
    node.removeAttribute("data-html-lore-editing-text");
    node.removeAttribute("contenteditable");
  });
  return `<!doctype html>\n${clone.outerHTML}`;
}
