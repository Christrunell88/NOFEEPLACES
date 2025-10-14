// NoFeePlaces WordMark Component - Standalone Version
// Can be used in any React project or converted to other formats

const NoFeePlacesWordMark = ({ 
  theme = 'dark',  // 'dark' or 'light'
  size = 'medium', // 'small', 'medium', 'large'
  tagline = 'NYC RENTAL PLATFORM'
}) => {
  
  const sizeConfig = {
    small: { main: 'text-2xl', sub: 'text-sm' },
    medium: { main: 'text-4xl', sub: 'text-xl' },
    large: { main: 'text-6xl', sub: 'text-3xl' }
  };

  const themeConfig = {
    dark: {
      no: 'text-white',
      fee: 'text-emerald-400', 
      places: 'text-gray-300',
      tagline: 'text-gray-400',
      underline: 'from-emerald-400/60 via-blue-400/40 to-transparent'
    },
    light: {
      no: 'text-gray-800',
      fee: 'text-emerald-600',
      places: 'text-gray-600', 
      tagline: 'text-gray-500',
      underline: 'from-emerald-600/50 via-blue-500/30 to-transparent'
    }
  };

  const config = sizeConfig[size];
  const colors = themeConfig[theme];

  return (
    <div className="flex flex-col">
      {/* Main Wordmark */}
      <div className="flex items-baseline space-x-0">
        <span className={`${config.main} font-extralight ${colors.no} tracking-wide`}>
          No
        </span>
        <span className={`${config.main} font-bold ${colors.fee} tracking-tight`}>
          Fee
        </span>
        <span className={`${config.sub} font-light ${colors.places} tracking-[0.2em] ml-2 mt-1`}>
          PLACES
        </span>
      </div>
      
      {/* Underline */}
      <div className={`w-full h-0.5 bg-gradient-to-r ${colors.underline} mt-1`}></div>
      
      {/* Tagline */}
      <div className={`text-xs ${colors.tagline} font-medium tracking-widest mt-1`}>
        {tagline}
      </div>
    </div>
  );
};

// Usage Examples:
// <NoFeePlacesWordMark theme="dark" size="large" />
// <NoFeePlacesWordMark theme="light" size="medium" tagline="ZERO BROKER FEES" />

export default NoFeePlacesWordMark;

/*
CSS VERSION (if you need pure CSS/HTML):

.nofee-wordmark {
  font-family: system-ui, -apple-system, sans-serif;
  display: flex;
  flex-direction: column;
}

.nofee-text {
  display: flex;
  align-items: baseline;
}

.nofee-no {
  font-size: 2.5rem;
  font-weight: 200;
  color: white; /* or #1f2937 for light theme */
  letter-spacing: 0.05em;
}

.nofee-fee {
  font-size: 2.5rem; 
  font-weight: 700;
  color: #10b981; /* emerald-500 */
  letter-spacing: -0.025em;
}

.nofee-places {
  font-size: 1.25rem;
  font-weight: 300;
  color: #d1d5db; /* gray-300 */
  letter-spacing: 0.2em;
  margin-left: 0.5rem;
  margin-top: 0.25rem;
}

.nofee-underline {
  width: 100%;
  height: 2px;
  background: linear-gradient(to right, rgba(16, 185, 129, 0.6), rgba(59, 130, 246, 0.4), transparent);
  margin-top: 0.25rem;
}

.nofee-tagline {
  font-size: 0.75rem;
  color: #9ca3af; /* gray-400 */
  font-weight: 500;
  letter-spacing: 0.1em;
  margin-top: 0.25rem;
}
*/