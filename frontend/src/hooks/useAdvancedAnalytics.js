import { useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import ReactGA from 'react-ga4';
import { hotjar } from 'react-hotjar';

// Advanced Analytics Hook for comprehensive tracking
export const useAdvancedAnalytics = () => {
  const location = useLocation();
  
  useEffect(() => {
    // Initialize all analytics services
    initializeAnalytics();
  }, []);

  useEffect(() => {
    // Track page views on route changes
    trackPageView(location.pathname + location.search);
  }, [location]);

  const initializeAnalytics = useCallback(() => {
    // Google Analytics 4 - already initialized in HTML
    console.log('✅ Google Analytics 4 initialized');
    
    // Hotjar initialization
    if (process.env.NODE_ENV === 'production') {
      hotjar.initialize(3849123, 6);
      console.log('✅ Hotjar initialized');
    }
    
    // Facebook Pixel - already initialized in HTML
    console.log('✅ Facebook Pixel initialized');
  }, []);

  const trackPageView = useCallback((path) => {
    // Google Analytics page view
    if (window.gtag) {
      window.gtag('config', 'G-NFEEPLACES123', {
        page_path: path,
        page_title: document.title,
        page_location: window.location.href
      });
    }

    // Facebook Pixel page view
    if (window.fbq) {
      window.fbq('track', 'PageView');
    }

    // Hotjar state change for SPA
    if (hotjar.initialized?.()) {
      hotjar.stateChange(path);
    }
  }, []);

  // Enhanced event tracking across all platforms
  const trackEvent = useCallback((eventName, properties = {}) => {
    const eventData = {
      action: eventName,
      category: properties.category || 'User Interaction',
      label: properties.label || '',
      value: properties.value || 0,
      ...properties
    };

    // Google Analytics 4 event
    if (window.gtag) {
      window.gtag('event', eventName, {
        event_category: eventData.category,
        event_label: eventData.label,
        value: eventData.value,
        custom_parameter_1: properties.apartmentType || '',
        custom_parameter_2: properties.neighborhood || '',
        user_engagement: true
      });
    }

    // Facebook Pixel event mapping
    const fbEventMap = {
      'apartment_view': 'ViewContent',
      'lead_generated': 'Lead',
      'form_submit': 'Lead',
      'email_signup': 'CompleteRegistration',
      'phone_call': 'Contact',
      'search_apartments': 'Search'
    };

    const fbEventName = fbEventMap[eventName] || eventName;
    if (window.fbq) {
      window.fbq('track', fbEventName, {
        content_name: properties.label || eventName,
        content_category: properties.category || 'apartment',
        value: properties.value || 0,
        currency: 'USD'
      });
    }

    // Hotjar event
    if (hotjar.initialized?.()) {
      hotjar.event(eventName);
    }

    console.log(`📊 Event tracked: ${eventName}`, eventData);
  }, []);

  // Apartment-specific tracking
  const trackApartmentView = useCallback((apartmentData) => {
    trackEvent('apartment_view', {
      category: 'Apartment Engagement',
      label: `${apartmentData.neighborhood} - ${apartmentData.bedrooms}BR`,
      value: apartmentData.rent || 0,
      apartmentType: `${apartmentData.bedrooms}BR`,
      neighborhood: apartmentData.neighborhood,
      rent: apartmentData.rent,
      apartment_id: apartmentData.id
    });
  }, [trackEvent]);

  const trackLeadGeneration = useCallback((leadData) => {
    trackEvent('lead_generated', {
      category: 'Lead Generation',
      label: leadData.source || 'website',
      value: leadData.estimatedValue || 100,
      lead_type: leadData.type,
      apartment_interest: leadData.apartmentId || ''
    });
  }, [trackEvent]);

  const trackSearch = useCallback((searchData) => {
    trackEvent('search_apartments', {
      category: 'Search',
      label: `${searchData.location} - ${searchData.priceRange}`,
      search_term: searchData.location,
      price_filter: searchData.priceRange,
      bedroom_filter: searchData.bedrooms
    });
  }, [trackEvent]);

  const trackUserEngagement = useCallback((engagementType, data = {}) => {
    const engagementEvents = {
      scroll_depth: 'scroll_engagement',
      time_on_page: 'time_engagement',
      click_through: 'click_engagement',
      social_share: 'social_engagement'
    };

    const eventName = engagementEvents[engagementType] || engagementType;
    trackEvent(eventName, {
      category: 'User Engagement',
      ...data
    });
  }, [trackEvent]);

  // Conversion tracking
  const trackConversion = useCallback((conversionType, conversionData = {}) => {
    trackEvent('conversion', {
      category: 'Conversions',
      label: conversionType,
      value: conversionData.value || 0,
      conversion_type: conversionType,
      ...conversionData
    });

    // Enhanced Facebook Pixel conversion tracking
    if (window.fbq) {
      const fbConversionMap = {
        'email_signup': 'CompleteRegistration',
        'phone_call': 'Contact',
        'tour_request': 'Schedule',
        'application_submit': 'SubmitApplication'
      };

      const fbEvent = fbConversionMap[conversionType] || 'Lead';
      window.fbq('track', fbEvent, {
        value: conversionData.value || 0,
        currency: 'USD',
        content_name: conversionType
      });
    }
  }, [trackEvent]);

  // Enhanced user identification for personalization
  const identifyUser = useCallback((userData) => {
    // Hotjar user identification
    if (hotjar.initialized?.()) {
      hotjar.identify(userData.id, {
        email: userData.email,
        user_type: userData.type || 'visitor',
        signup_date: userData.signupDate,
        preferred_neighborhood: userData.preferences?.neighborhood,
        budget_range: userData.preferences?.budgetRange
      });
    }

    // Google Analytics user properties
    if (window.gtag) {
      window.gtag('config', 'G-NFEEPLACES123', {
        user_id: userData.id,
        custom_parameter_1: userData.preferences?.apartmentType || '',
        custom_parameter_2: userData.preferences?.neighborhood || ''
      });
    }

    console.log('👤 User identified for analytics:', userData.id);
  }, []);

  return {
    trackEvent,
    trackApartmentView,
    trackLeadGeneration,
    trackSearch,
    trackUserEngagement,
    trackConversion,
    identifyUser
  };
};

// Analytics context for app-wide usage
import React, { createContext, useContext } from 'react';

const AnalyticsContext = createContext();

export const AnalyticsProvider = ({ children }) => {
  const analytics = useAdvancedAnalytics();

  return (
    <AnalyticsContext.Provider value={analytics}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};