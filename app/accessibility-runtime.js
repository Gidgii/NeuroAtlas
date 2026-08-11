let shortcutsInstalled = false;

export function focusMainHeading(main) {
  const target = main?.querySelector('h1');
  if (!target) return;
  target.setAttribute('tabindex', '-1');
  setTimeout(() => target.focus({preventScroll: true}), 0);
}

export function installAccessibilityRuntime({searchButton}) {
  if (shortcutsInstalled) return;
  shortcutsInstalled = true;
  document.addEventListener('keydown', event => {
    const target = event.target;
    const typing = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target?.isContentEditable;
    if (event.key === '/' && !typing && !event.metaKey && !event.ctrlKey && !event.altKey) {
      event.preventDefault();
      searchButton?.click();
    }
  });
}
