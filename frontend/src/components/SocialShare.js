import React, { useState } from 'react';
import {
  FacebookShareButton,
  TwitterShareButton,
  WhatsappShareButton,
  FacebookIcon,
  TwitterIcon,
  WhatsappIcon
} from 'react-share';
import { useAnalytics } from '../hooks/useAdvancedAnalytics';

// Social Share Component for apartments and general content
export const SocialShare = ({ 
  url, 
  title, 
  description, 
  apartment = null,
  className = '',
  showLabels = true,
  size = 32 
}) => {
  const { trackUserEngagement } = useAnalytics();
  const [shareCount, setShareCount] = useState(0);

  const shareUrl = url || window.location.href;
  const shareTitle = title || 'Check out this amazing no-fee apartment in NYC!';
  const shareDescription = description || 'Found on NoFeePlaces.com - NYC\'s #1 platform for no-fee apartments';

  // Enhanced sharing with apartment details
  const getApartmentShareText = () => {
    if (!apartment) return shareDescription;

    return `🏠 ${apartment.bedrooms}BR apartment in ${apartment.neighborhood} - $${apartment.rent}/month - NO BROKER FEES! Found on NoFeePlaces.com`;
  };

  const handleShare = (platform) => {
    setShareCount(prev => prev + 1);
    
    // Track social sharing
    trackUserEngagement('social_share', {
      platform: platform,
      content_type: apartment ? 'apartment' : 'general',
      apartment_id: apartment?.id,
      share_url: shareUrl
    });

    console.log(`📱 Content shared on ${platform}`);
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {showLabels && (
        <span className="text-sm font-medium text-gray-700">Share:</span>
      )}
      
      {/* Facebook Share */}
      <FacebookShareButton
        url={shareUrl}
        quote={apartment ? getApartmentShareText() : shareTitle}
        hashtag="#NoFeeApartmentsNYC"
        onShareWindowClose={() => handleShare('facebook')}
        className="hover:opacity-80 transition-opacity"
      >
        <FacebookIcon size={size} round />
      </FacebookShareButton>

      {/* Twitter Share */}
      <TwitterShareButton
        url={shareUrl}
        title={apartment ? getApartmentShareText() : shareTitle}
        hashtags={['NoFeeApartmentsNYC', 'NYCRentals', 'NoBrokerFee']}
        via="NoFeePlacesNYC"
        onShareWindowClose={() => handleShare('twitter')}
        className="hover:opacity-80 transition-opacity"
      >
        <TwitterIcon size={size} round />
      </TwitterShareButton>

      {/* WhatsApp Share */}
      <WhatsappShareButton
        url={shareUrl}
        title={apartment ? getApartmentShareText() : `${shareTitle} - ${shareDescription}`}
        separator=" - "
        onShareWindowClose={() => handleShare('whatsapp')}
        className="hover:opacity-80 transition-opacity"
      >
        <WhatsappIcon size={size} round />
      </WhatsappShareButton>

      {/* Phone Call Button for direct contact */}
      <a
        href="tel:646-408-8048"
        onClick={() => handleShare('phone')}
        className="inline-flex items-center justify-center w-8 h-8 bg-green-500 text-white rounded-full hover:bg-green-600 transition-colors"
        title="Call us directly"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
      </a>

      {shareCount > 0 && (
        <span className="text-xs text-gray-500 ml-2">
          Shared {shareCount} time{shareCount !== 1 ? 's' : ''}
        </span>
      )}
    </div>
  );
};

// Floating Social Share Widget
export const FloatingSocialShare = ({ apartment = null }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className={`transition-all duration-300 ${isExpanded ? 'mb-4' : ''}`}>
        {isExpanded && (
          <div className="bg-white rounded-lg shadow-lg p-4 mb-3">
            <div className="text-sm font-medium text-gray-900 mb-3">
              {apartment ? 'Share this apartment:' : 'Share NoFeePlaces.com:'}
            </div>
            <SocialShare 
              apartment={apartment}
              showLabels={false}
              size={40}
            />
          </div>
        )}
      </div>
      
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        aria-label="Share options"
      >
        {isExpanded ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
        )}
      </button>
    </div>
  );
};

// Instagram Share Component (custom implementation)
export const InstagramShare = ({ imageUrl, caption, className = '' }) => {
  const { trackUserEngagement } = useAnalytics();

  const handleInstagramShare = () => {
    // Track Instagram share intent
    trackUserEngagement('social_share', {
      platform: 'instagram',
      content_type: 'image'
    });

    // Open Instagram web with share intent
    const instagramUrl = `https://www.instagram.com/create/select/`;
    window.open(instagramUrl, '_blank');
    
    // Show user instructions
    alert('📸 Instagram Share:\n\n1. Upload your screenshot\n2. Use this caption:\n\n' + caption + '\n\n3. Tag @NoFeePlacesNYC\n4. Use hashtags: #NoFeeApartmentsNYC #NYCRentals');
  };

  return (
    <button
      onClick={handleInstagramShare}
      className={`inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 ${className}`}
    >
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12.017 0C8.396 0 7.989.013 6.756.072 5.526.13 4.74.333 4.077.63a5.947 5.947 0 0 0-2.148 1.4A5.957 5.957 0 0 0 .531 4.177c-.297.663-.5 1.45-.558 2.679C-.085 8.089-.072 8.495-.072 12.116c0 3.621-.013 4.027.072 5.26.058 1.23.26 2.016.558 2.68.298.662.733 1.224 1.4 2.147A5.96 5.96 0 0 0 4.077 23.6c.663.296 1.449.499 2.679.557 1.233.059 1.639.072 5.26.072 3.622 0 4.028-.013 5.26-.072 1.23-.058 2.017-.261 2.68-.557a5.948 5.948 0 0 0 2.147-1.4 5.955 5.955 0 0 0 1.4-2.148c.296-.663.499-1.449.557-2.679.059-1.233.072-1.639.072-5.26 0-3.621.013-4.027-.072-5.26-.058-1.23-.261-2.016-.557-2.68a5.955 5.955 0 0 0-1.4-2.147A5.947 5.947 0 0 0 19.683.63C19.02.333 18.234.13 17.003.072 15.77.013 15.364 0 11.743 0h.274zM10.94 2.179c.311-.003.66-.003 1.077-.003 3.564 0 3.986.012 5.39.071 1.3.059 2.006.274 2.477.456.623.242 1.068.531 1.537 1.001.47.47.76.914 1.001 1.537.182.471.397 1.177.456 2.477.059 1.404.071 1.826.071 5.39 0 3.564-.012 3.986-.071 5.39-.059 1.3-.274 2.006-.456 2.477a4.142 4.142 0 0 1-1.001 1.537c-.47.47-.914.76-1.537 1.001-.471.182-1.177.397-2.477.456-1.404.059-1.826.071-5.39.071-3.564 0-3.986-.012-5.39-.071-1.3-.059-2.006-.274-2.477-.456a4.142 4.142 0 0 1-1.537-1.001 4.142 4.142 0 0 1-1.001-1.537c-.182-.471-.397-1.177-.456-2.477-.059-1.404-.071-1.826-.071-5.39 0-3.564.012-3.986.071-5.39.059-1.3.274-2.006.456-2.477.242-.623.531-1.068 1.001-1.537.47-.47.914-.76 1.537-1.001.471-.182 1.177-.397 2.477-.456 1.228-.056 1.704-.069 4.313-.07v.002zm8.556 2.254a1.33 1.33 0 1 0 0 2.66 1.33 1.33 0 0 0 0-2.66zm-7.496 1.967c-3.996 0-7.236 3.24-7.236 7.236s3.24 7.236 7.236 7.236 7.236-3.24 7.236-7.236-3.24-7.236-7.236-7.236zm0 2.598a4.638 4.638 0 1 1 0 9.276 4.638 4.638 0 0 1 0-9.276z" />
      </svg>
      <span>Share on Instagram</span>
    </button>
  );
};