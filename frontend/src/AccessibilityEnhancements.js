import React from 'react';

// Accessibility-enhanced components
export const SkipLink = () => (
  <a 
    href="#main-content" 
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-lg z-50 focus:outline-none focus:ring-2 focus:ring-blue-300"
  >
    Skip to main content
  </a>
);

export const ScreenReaderOnly = ({ children }) => (
  <span className="sr-only">{children}</span>
);

// Enhanced button with proper accessibility
export const AccessibleButton = ({ 
  children, 
  onClick, 
  ariaLabel, 
  ariaExpanded, 
  className = "",
  disabled = false,
  type = "button",
  ...props 
}) => (
  <button
    type={type}
    onClick={onClick}
    aria-label={ariaLabel}
    aria-expanded={ariaExpanded}
    disabled={disabled}
    className={`focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className}`}
    {...props}
  >
    {children}
  </button>
);

// Enhanced link with proper accessibility
export const AccessibleLink = ({ 
  children, 
  to, 
  href, 
  ariaLabel, 
  className = "",
  external = false,
  ...props 
}) => {
  const linkProps = {
    'aria-label': ariaLabel,
    className: `focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className}`,
    ...(external && { 
      target: "_blank", 
      rel: "noopener noreferrer",
      'aria-label': `${ariaLabel || children} (opens in new tab)`
    }),
    ...props
  };

  if (to) {
    const { Link } = require('react-router-dom');
    return <Link to={to} {...linkProps}>{children}</Link>;
  }
  
  return <a href={href} {...linkProps}>{children}</a>;
};

// Enhanced form components
export const AccessibleInput = ({ 
  label, 
  id, 
  error, 
  required = false, 
  describedBy,
  ...props 
}) => (
  <div className="mb-4">
    <label 
      htmlFor={id} 
      className="block text-sm font-medium text-gray-700 mb-2"
    >
      {label}
      {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
    </label>
    <input
      id={id}
      aria-required={required}
      aria-invalid={!!error}
      aria-describedby={error ? `${id}-error` : describedBy}
      className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
        error ? 'border-red-500' : 'border-gray-300'
      }`}
      {...props}
    />
    {error && (
      <div id={`${id}-error`} className="mt-1 text-sm text-red-600" role="alert">
        {error}
      </div>
    )}
  </div>
);

// Modal with proper focus management
export const AccessibleModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  className = "" 
}) => {
  React.useEffect(() => {
    if (isOpen) {
      // Focus the modal when it opens
      const modal = document.getElementById('modal-dialog');
      if (modal) modal.focus();
      
      // Trap focus within modal
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          onClose();
        }
        
        if (e.key === 'Tab') {
          const focusableElements = modal?.querySelectorAll(
            'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
          );
          const firstElement = focusableElements?.[0];
          const lastElement = focusableElements?.[focusableElements.length - 1];

          if (e.shiftKey && document.activeElement === firstElement) {
            lastElement?.focus();
            e.preventDefault();
          } else if (!e.shiftKey && document.activeElement === lastElement) {
            firstElement?.focus();
            e.preventDefault();
          }
        }
      };
      
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      role="dialog" 
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <div 
        id="modal-dialog"
        tabIndex={-1}
        className={`bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto focus:outline-none ${className}`}
      >
        <div className="p-6">
          {title && (
            <h2 id="modal-title" className="text-xl font-bold text-gray-900 mb-4">
              {title}
            </h2>
          )}
          {children}
        </div>
      </div>
    </div>
  );
};

// Loading state with proper announcements
export const AccessibleLoadingState = ({ message = "Loading..." }) => (
  <div 
    role="status" 
    aria-live="polite"
    className="flex items-center justify-center p-4"
  >
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mr-3"></div>
    <span>{message}</span>
  </div>
);

// Alert component for announcements
export const AccessibleAlert = ({ 
  type = "info", 
  children, 
  dismissible = false, 
  onDismiss 
}) => {
  const typeClasses = {
    info: "bg-blue-50 border-blue-200 text-blue-700",
    success: "bg-green-50 border-green-200 text-green-700", 
    warning: "bg-yellow-50 border-yellow-200 text-yellow-700",
    error: "bg-red-50 border-red-200 text-red-700"
  };

  return (
    <div 
      role="alert"
      className={`border rounded-lg p-4 ${typeClasses[type]}`}
    >
      <div className="flex items-center justify-between">
        <div>{children}</div>
        {dismissible && (
          <button
            onClick={onDismiss}
            aria-label="Dismiss alert"
            className="ml-4 text-current hover:text-opacity-75 focus:outline-none focus:ring-2 focus:ring-current focus:ring-offset-2 rounded"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default {
  SkipLink,
  ScreenReaderOnly,
  AccessibleButton,
  AccessibleLink,
  AccessibleInput,
  AccessibleModal,
  AccessibleLoadingState,
  AccessibleAlert
};