
export function SkipNavigation() {
  return (
    <div className="sr-only-focusable">
      <a
        href="#main-content"
        className="skip-link"
        onFocus={(e) => {
          e.currentTarget.classList.remove('sr-only');
        }}
        onBlur={(e) => {
          e.currentTarget.classList.add('sr-only');
        }}
      >
        Skip to main content
      </a>
      <a
        href="#main-navigation"
        className="skip-link"
        style={{ left: '200px' }}
        onFocus={(e) => {
          e.currentTarget.classList.remove('sr-only');
        }}
        onBlur={(e) => {
          e.currentTarget.classList.add('sr-only');
        }}
      >
        Skip to navigation
      </a>
    </div>
  );
}
