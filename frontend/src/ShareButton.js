import React, { useState } from 'react';

const ShareButton = ({ apartment, size = 'md', variant = 'icon', className = '' }) => {
  const [showModal, setShowModal] = useState(false);

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  // Full button variant for modal detail views
  if (variant === 'full') {
    return (
      <>
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowModal(true);
          }}
          className={`w-full bg-white border border-blue-300 text-blue-600 py-3 px-4 rounded hover:bg-blue-50 transition-colors font-medium flex items-center justify-center gap-2 ${className}`}
          aria-label="Share listing"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          Share Listing
        </button>

        {showModal && (
          <ShareModal 
            apartment={apartment}
            onClose={() => setShowModal(false)}
          />
        )}
      </>
    );
  }

  // Icon button variant for cards
  return (
    <>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setShowModal(true);
        }}
        className={`${sizeClasses[size]} flex items-center justify-center bg-white rounded-full shadow-lg hover:scale-110 transition-transform hover:bg-blue-50 ${className}`}
        title="Share this listing"
        aria-label="Share listing"
      >
        <svg 
          className={`${iconSizes[size]} text-blue-600`}
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" 
          />
        </svg>
      </button>

      {showModal && (
        <ShareModal 
          apartment={apartment}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
};

// ShareModal Component
const ShareModal = ({ apartment, onClose }) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
  const DOMAIN_URL = process.env.REACT_APP_DOMAIN_URL || 'https://nofeeplaces.com';
  const shareUrl = `${DOMAIN_URL}/apartment/${apartment.id}`;
  
  // Facebook Page ID for Places NYC: 164228704193646
  const FACEBOOK_PAGE_ID = '164228704193646';

  const handleEmailShare = async (e) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      showNotification('Please enter a valid email address', 'error');
      return;
    }

    setLoading(true);

    try {
      // Get user info if authenticated
      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

      const response = await fetch(`${BACKEND_URL}/api/apartments/${apartment.id}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify({
          recipient_email: email
        })
      });

      if (response.ok) {
        showNotification('Listing shared successfully!', 'success');
        setEmail('');
        setTimeout(() => onClose(), 1500);
      } else {
        const data = await response.json();
        showNotification(data.detail || 'Failed to share listing', 'error');
      }
    } catch (err) {
      console.error('Error sharing listing:', err);
      showNotification('Failed to share listing. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = async () => {
    let copySuccessful = false;
    
    // Try modern Clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(shareUrl);
        copySuccessful = true;
      } catch (err) {
        console.log('Clipboard API failed, trying fallback method:', err.message);
        // Don't return here, let it fall through to fallback
      }
    }
    
    // If modern API failed or isn't available, use fallback method
    if (!copySuccessful) {
      try {
        const textArea = document.createElement('textarea');
        textArea.value = shareUrl;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          copySuccessful = true;
        } else {
          throw new Error('Fallback copy command failed');
        }
      } catch (err) {
        console.error('Fallback copy failed:', err);
        showNotification('Failed to copy link. Please copy manually: ' + shareUrl, 'error');
        return;
      }
    }
    
    // If we get here, copy was successful
    if (copySuccessful) {
      setCopySuccess(true);
      showNotification('Link copied to clipboard!', 'success');
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleSocialShare = async (platform) => {
    const text = `Check out this ${apartment.bedrooms === 0 ? 'Studio' : apartment.bedrooms + 'BR'} apartment in ${apartment.neighborhood || 'NYC'} - $${apartment.price}/mo - No Fee!`;
    
    // Try native Web Share API first (works great on mobile and some desktop browsers)
    if (platform === 'facebook' && navigator.share) {
      try {
        await navigator.share({
          title: text,
          text: `${text}\n\nView details:`,
          url: shareUrl
        });
        showNotification('Shared successfully!', 'success');
        return;
      } catch (err) {
        // User cancelled or share failed, fall through to traditional method
        if (err.name !== 'AbortError') {
          console.log('Web Share API failed, using fallback');
        }
      }
    }
    
    let url;
    switch(platform) {
      case 'whatsapp':
        url = `https://wa.me/?text=${encodeURIComponent(text + ' ' + shareUrl)}`;
        break;
      case 'facebook':
        // Facebook sharing - simplified approach
        // This opens Facebook's mobile-friendly share interface
        // Uses m.facebook.com which is more lenient than www.facebook.com
        url = `https://m.facebook.com/sharer.php?u=${encodeURIComponent(shareUrl)}&quote=${encodeURIComponent(text)}`;
        break;
      case 'twitter':
        url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`;
        break;
      default:
        return;
    }
    
    // For Facebook, try to open directly - no popup restrictions
    if (platform === 'facebook') {
      // Direct navigation - more reliable
      window.location.href = url;
    } else {
      // For other platforms, use new window
      const windowFeatures = 'width=600,height=500,left=100,top=100,resizable=yes,scrollbars=yes';
      const newWindow = window.open(url, '_blank', windowFeatures);
      
      // Fallback if popup is blocked
      if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
        window.open(url, '_blank');
      }
    }
  };

  const showNotification = (message, type) => {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-[60] transform transition-all duration-300 ${
      type === 'success' ? 'bg-green-500' : 'bg-red-500'
    }`;
    toast.textContent = message;
    toast.style.opacity = '0';
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '1';
    }, 10);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 300);
    }, 3000);
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg max-w-md w-full p-6 relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl leading-none"
          aria-label="Close"
        >
          ×
        </button>

        {/* Header */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Share This Listing
          </h2>
          <p className="text-gray-600 text-sm">
            {apartment.bedrooms === 0 ? 'Studio' : `${apartment.bedrooms}BR`} in {apartment.neighborhood || 'NYC'} - ${apartment.price?.toLocaleString()}/mo
          </p>
        </div>

        {/* Email Share */}
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Share via Email
          </h3>
          <form onSubmit={handleEmailShare} className="space-y-3">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="friend@example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              style={{ color: '#111827' }}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Sending...' : 'Send Email'}
            </button>
          </form>
        </div>

        {/* Copy Link */}
        <div className="mb-6">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Copy Link
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
              style={{ color: '#111827' }}
            />
            <button
              onClick={handleCopyLink}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                copySuccess 
                  ? 'bg-green-600 text-white' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {copySuccess ? '✓' : 'Copy'}
            </button>
          </div>
        </div>

        {/* Social Media */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Share on Social Media
          </h3>
          <div className="flex gap-3">
            <button
              onClick={() => handleSocialShare('whatsapp')}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
              </svg>
              WhatsApp
            </button>
            <button
              onClick={() => handleSocialShare('facebook')}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
            <button
              onClick={() => handleSocialShare('twitter')}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
              Twitter
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShareButton;
