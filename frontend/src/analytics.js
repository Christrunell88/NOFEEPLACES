/**
 * Google Analytics 4 Event Tracking for NoFeePlaces.com
 * Comprehensive tracking for apartment searches, views, contacts, and user engagement
 */

// Check if gtag is available (production environment)
const isGtagAvailable = () => {
  return typeof window !== 'undefined' && typeof window.gtag === 'function';
};

// Generic event tracking function
export const trackEvent = (eventName, parameters = {}) => {
  if (isGtagAvailable()) {
    window.gtag('event', eventName, {
      event_category: 'NoFeePlaces_Engagement',
      event_label: parameters.label || '',
      value: parameters.value || 0,
      ...parameters
    });
    console.log(`📊 GA4 Event: ${eventName}`, parameters);
  } else {
    console.log(`📊 GA4 Event (dev): ${eventName}`, parameters);
  }
};

// Page view tracking with visitor notification
export const trackPageView = (pagePath, pageTitle) => {
  if (isGtagAvailable()) {
    window.gtag('config', 'G-XMDGXKJJ8M', {
      page_path: pagePath,
      page_title: pageTitle,
    });
    console.log(`📊 GA4 Page View: ${pageTitle} (${pagePath})`);
  }
  
  // Send visitor notification to admin (only for homepage visits)
  if (pagePath === '/' || pagePath === '' || !pagePath) {
    trackVisitorArrival();
  }
};

// Track visitor arrival and send email notification
export const trackVisitorArrival = async () => {
  try {
    const API_URL = process.env.REACT_APP_BACKEND_URL || 'https://affordable-apts.emergent.host';
    
    const response = await fetch(`${API_URL}/api/visitor/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        page: window.location.pathname,
        referrer: document.referrer || 'direct'
      })
    });
    
    if (response.ok) {
      console.log('📧 Visitor tracking notification sent');
    } else {
      console.log('⚠️ Visitor tracking failed');
    }
  } catch (error) {
    console.log('⚠️ Visitor tracking error:', error);
  }
};

// Apartment-specific tracking events
export const trackApartmentView = (apartment) => {
  trackEvent('apartment_view', {
    event_category: 'Apartment_Engagement',
    apartment_id: apartment.id,
    apartment_price: apartment.price,
    apartment_bedrooms: apartment.bedrooms,
    apartment_borough: apartment.borough,
    apartment_neighborhood: apartment.neighborhood,
    label: `${apartment.title} - $${apartment.price}`,
    value: apartment.price
  });
};

export const trackApartmentSearch = (searchParams) => {
  trackEvent('apartment_search', {
    event_category: 'Search_Activity',
    search_term: searchParams.search || '',
    min_price: searchParams.min_price || 0,
    max_price: searchParams.max_price || 0,
    bedrooms: searchParams.bedrooms || '',
    borough: searchParams.borough || '',
    neighborhood: searchParams.neighborhood || '',
    label: `Search: ${searchParams.search || 'All apartments'}`,
    value: 1
  });
};

export const trackContactForm = (contactData, apartment) => {
  trackEvent('contact_form_submission', {
    event_category: 'Lead_Generation',
    apartment_id: contactData.apartment_id,
    apartment_price: apartment?.price || 0,
    contact_method: contactData.preferred_contact || 'email',
    has_phone: !!contactData.phone,
    has_message: !!contactData.message,
    label: `Contact: ${apartment?.title || 'Unknown apartment'}`,
    value: apartment?.price || 0
  });
};

// User engagement tracking
export const trackNewsletterSignup = (email, source = 'website') => {
  trackEvent('newsletter_signup', {
    event_category: 'User_Engagement',
    signup_source: source,
    label: `Newsletter signup from ${source}`,
    value: 1
  });
};

export const trackUserAuthentication = (method, action) => {
  trackEvent('user_authentication', {
    event_category: 'User_Management',
    auth_method: method, // 'google', 'email', etc.
    auth_action: action, // 'login', 'register', 'logout'
    label: `${action} via ${method}`,
    value: 1
  });
};

// Search and filter tracking
export const trackFilterUsage = (filterType, filterValue) => {
  trackEvent('filter_usage', {
    event_category: 'Search_Activity',
    filter_type: filterType, // 'price', 'bedrooms', 'borough', etc.
    filter_value: filterValue,
    label: `Filter: ${filterType} = ${filterValue}`,
    value: 1
  });
};

// Hero and navigation tracking
export const trackHeroAction = (action, buttonText) => {
  trackEvent('hero_action', {
    event_category: 'Hero_Engagement',
    action_type: action, // 'cta_click', 'scroll', 'search'
    button_text: buttonText,
    label: `Hero: ${action} - ${buttonText}`,
    value: 1
  });
};

export const trackNavigationClick = (navItem, destination) => {
  trackEvent('navigation_click', {
    event_category: 'Navigation',
    nav_item: navItem,
    destination: destination,
    label: `Nav: ${navItem} → ${destination}`,
    value: 1
  });
};

// Performance and error tracking
export const trackPerformanceMetric = (metricName, value, unit = 'ms') => {
  trackEvent('performance_metric', {
    event_category: 'Performance',
    metric_name: metricName,
    metric_value: value,
    metric_unit: unit,
    label: `Performance: ${metricName} = ${value}${unit}`,
    value: value
  });
};

export const trackError = (errorType, errorMessage, component) => {
  trackEvent('application_error', {
    event_category: 'Errors',
    error_type: errorType,
    error_message: errorMessage,
    component: component,
    label: `Error: ${errorType} in ${component}`,
    value: 1
  });
};

// Business intelligence tracking
export const trackBusinessMetric = (metricName, value, context) => {
  trackEvent('business_metric', {
    event_category: 'Business_Intelligence',
    metric_name: metricName,
    metric_value: value,
    context: context,
    label: `Business: ${metricName} = ${value}`,
    value: value
  });
};

// Enhanced ecommerce-style tracking for apartment listings
export const trackListingImpression = (apartments, listContext) => {
  if (isGtagAvailable() && apartments.length > 0) {
    const items = apartments.slice(0, 10).map((apt, index) => ({
      item_id: apt.id,
      item_name: apt.title,
      item_category: 'Apartment',
      item_category2: apt.borough,
      item_category3: apt.neighborhood,
      price: apt.price,
      quantity: 1,
      index: index,
      item_brand: 'NoFeePlaces'
    }));

    window.gtag('event', 'view_item_list', {
      item_list_id: listContext,
      item_list_name: `Apartment Listings - ${listContext}`,
      items: items
    });
    
    console.log(`📊 GA4 Listing Impressions: ${items.length} apartments in ${listContext}`);
  }
};

// Conversion tracking
export const trackConversion = (conversionType, value, apartmentId) => {
  trackEvent('conversion', {
    event_category: 'Conversions',
    conversion_type: conversionType, // 'contact_submitted', 'phone_revealed', 'email_sent'
    apartment_id: apartmentId,
    conversion_value: value,
    label: `Conversion: ${conversionType}`,
    value: value
  });
  
  // Also track as GA4 conversion event
  if (isGtagAvailable()) {
    window.gtag('event', 'generate_lead', {
      currency: 'USD',
      value: value
    });
  }
};

export default {
  trackEvent,
  trackPageView,
  trackApartmentView,
  trackApartmentSearch,
  trackContactForm,
  trackNewsletterSignup,
  trackUserAuthentication,
  trackFilterUsage,
  trackHeroAction,
  trackNavigationClick,
  trackPerformanceMetric,
  trackError,
  trackBusinessMetric,
  trackListingImpression,
  trackConversion
};