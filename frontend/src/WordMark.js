import React from 'react';
import { Link } from 'react-router-dom';

// Reusable WordMark component with different size variants
export const WordMark = ({ 
  size = 'medium', 
  theme = 'dark', 
  showTagline = true, 
  tagline = null,
  linkTo = "/",
  className = "",
  hover = true
}) => {
  
  // Size configurations
  const sizeConfigs = {
    small: {
      noSize: 'text-lg',
      feeSize: 'text-lg', 
      placesSize: 'text-sm',
      taglineSize: 'text-xs',
      spacing: 'space-x-0',
      underlineHeight: 'h-0.5',
      taglineMargin: 'mt-0.5'
    },
    medium: {
      noSize: 'text-3xl',
      feeSize: 'text-3xl',
      placesSize: 'text-lg',
      taglineSize: 'text-xs',
      spacing: 'space-x-0',
      underlineHeight: 'h-0.5',
      taglineMargin: 'mt-1'
    },
    large: {
      noSize: 'text-5xl',
      feeSize: 'text-5xl',
      placesSize: 'text-2xl',
      taglineSize: 'text-sm',
      spacing: 'space-x-0',
      underlineHeight: 'h-1',
      taglineMargin: 'mt-2'
    },
    xlarge: {
      noSize: 'text-6xl',
      feeSize: 'text-6xl',
      placesSize: 'text-3xl',
      taglineSize: 'text-base',
      spacing: 'space-x-0',
      underlineHeight: 'h-1',
      taglineMargin: 'mt-3'
    }
  };

  // Theme configurations
  const themeConfigs = {
    dark: {
      noColor: hover ? 'text-white group-hover:text-blue-200 transition-colors duration-300' : 'text-white',
      feeColor: hover ? 'text-emerald-400 group-hover:text-emerald-300 transition-colors duration-300' : 'text-emerald-400',
      placesColor: hover ? 'text-gray-300 group-hover:text-white transition-colors duration-300' : 'text-gray-300',
      taglineColor: hover ? 'text-gray-400 group-hover:text-gray-300 transition-colors duration-300' : 'text-gray-400',
      underlineGradient: hover ? 'from-emerald-400/60 via-blue-400/40 to-transparent group-hover:from-emerald-400/80 group-hover:via-blue-400/60 transition-all duration-300' : 'from-emerald-400/60 via-blue-400/40 to-transparent'
    },
    light: {
      noColor: hover ? 'text-gray-800 group-hover:text-gray-700 transition-colors duration-300' : 'text-gray-800',
      feeColor: hover ? 'text-emerald-600 group-hover:text-emerald-700 transition-colors duration-300' : 'text-emerald-600',
      placesColor: hover ? 'text-gray-600 group-hover:text-gray-800 transition-colors duration-300' : 'text-gray-600',
      taglineColor: hover ? 'text-gray-500 group-hover:text-gray-600 transition-colors duration-300' : 'text-gray-500',
      underlineGradient: hover ? 'from-emerald-600/50 via-blue-500/30 to-transparent group-hover:from-emerald-600/70 group-hover:via-blue-500/50 transition-all duration-300' : 'from-emerald-600/50 via-blue-500/30 to-transparent'
    },
    white: {
      noColor: hover ? 'text-white group-hover:text-blue-100 transition-colors duration-300' : 'text-white',
      feeColor: hover ? 'text-emerald-300 group-hover:text-emerald-200 transition-colors duration-300' : 'text-emerald-300',
      placesColor: hover ? 'text-gray-200 group-hover:text-white transition-colors duration-300' : 'text-gray-200',
      taglineColor: hover ? 'text-gray-300 group-hover:text-gray-200 transition-colors duration-300' : 'text-gray-300',
      underlineGradient: hover ? 'from-emerald-300/60 via-blue-300/40 to-transparent group-hover:from-emerald-300/80 group-hover:via-blue-300/60 transition-all duration-300' : 'from-emerald-300/60 via-blue-300/40 to-transparent'
    }
  };

  const config = sizeConfigs[size];
  const themeConfig = themeConfigs[theme];
  const defaultTaglines = {
    dark: 'NYC RENTAL PLATFORM',
    light: 'NYC RENTAL PLATFORM', 
    white: 'NYC RENTAL PLATFORM'
  };

  const displayTagline = tagline || defaultTaglines[theme];

  const WordMarkContent = () => (
    <div className={`flex flex-col ${className}`}>
      {/* Main Wordmark */}
      <div className={`flex items-baseline ${config.spacing}`}>
        <span 
          className={`${config.noSize} font-extralight ${themeConfig.noColor} tracking-wide`}
          style={{fontFamily: 'system-ui, -apple-system, sans-serif'}}
        >
          No
        </span>
        <span 
          className={`${config.feeSize} font-bold ${themeConfig.feeColor} tracking-tight`}
          style={{fontFamily: 'system-ui, -apple-system, sans-serif'}}
        >
          Fee
        </span>
        <span 
          className={`${config.placesSize} font-light ${themeConfig.placesColor} tracking-[0.2em] ml-2 ${size === 'large' || size === 'xlarge' ? 'mt-2' : 'mt-1'}`}
          style={{fontFamily: 'system-ui, -apple-system, sans-serif'}}
        >
          PLACES
        </span>
      </div>
      
      {/* Subtle Underline */}
      <div className={`w-full ${config.underlineHeight} bg-gradient-to-r ${themeConfig.underlineGradient} ${config.taglineMargin}`}></div>
      
      {/* Tagline */}
      {showTagline && (
        <div className={`${config.taglineSize} ${themeConfig.taglineColor} font-medium tracking-widest ${config.taglineMargin}`}>
          {displayTagline}
        </div>
      )}
    </div>
  );

  // Return with or without Link based on linkTo prop
  if (linkTo) {
    return (
      <Link to={linkTo} className={hover ? "group" : ""}>
        <WordMarkContent />
      </Link>
    );
  }

  return <WordMarkContent />;
};

// Predefined variants for common use cases
export const HeaderWordMark = (props) => (
  <WordMark size="medium" theme="dark" tagline="NYC RENTAL PLATFORM" {...props} />
);

export const FooterWordMark = (props) => (
  <WordMark size="small" theme="dark" tagline="NYC RENTAL PLATFORM" {...props} />
);

export const HeroWordMark = (props) => (
  <WordMark size="xlarge" theme="white" tagline="ZERO BROKER FEES • PREMIUM RENTALS" {...props} />
);

export const PageWordMark = (props) => (
  <WordMark size="large" theme="light" tagline="NYC'S PREMIER NO-FEE APARTMENT PLATFORM" {...props} />
);

export default WordMark;