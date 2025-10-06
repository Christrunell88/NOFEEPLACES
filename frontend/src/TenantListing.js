import React, { useState, useEffect } from 'react';
import { useAuth } from './auth';
import axios from 'axios';
import { AuthModal } from './missing-components';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

// Tenant Apartment Listing Page
export const TenantListingPage = () => {
  const { isAuthenticated, user } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    rent_price: '',
    listing_type: 'sublet', // sublet, roommate, lease_transfer
    bedrooms: '',
    bathrooms: '',
    sqft: '',
    address: '',
    neighborhood: '',
    borough: 'Manhattan',
    available_date: '',
    lease_end_date: '',
    contact_name: user?.name || '',
    contact_email: user?.email || '',
    contact_phone: '',
    amenities: [],
    images: [],
    uploaded_image_files: [], // For actual file uploads
    utilities_included: false,
    pets_allowed: false,
    furnished: false,
    short_term_ok: false,
    deposit_required: '',
    additional_notes: ''
  });
  
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [imagePreview, setImagePreview] = useState([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Monitor authentication status changes
  useEffect(() => {
    if (isAuthenticated && user) {
      // Update form data with user information
      setFormData(prev => ({
        ...prev,
        contact_name: user.name || '',
        contact_email: user.email || ''
      }));
      setShowAuthModal(false); // Close auth modal when logged in
    }
  }, [isAuthenticated, user]);

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">🔐</div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Sign In Required
            </h2>
            <p className="text-gray-600 mb-6">
              You need to sign in to your NoFeePlaces account to list your apartment. This helps us verify listings and protect both tenants and landlords.
            </p>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-green-800 mb-2">Why Sign In?</h3>
              <ul className="text-sm text-green-700 space-y-1 text-left">
                <li>• Verify your identity for trusted listings</li>
                <li>• Track your listing status and inquiries</li>
                <li>• Upload photos directly to our secure platform</li>
                <li>• Edit your listing after submission</li>
                <li>• Get notifications when someone is interested</li>
              </ul>
            </div>
            <div className="space-y-3">
              <button
                onClick={() => setShowAuthModal(true)}
                className="w-full bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Sign In / Create Account
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="w-full bg-gray-200 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
              >
                Back to Homepage
              </button>
            </div>
          </div>
        </div>
        
        {/* Authentication Modal */}
        {showAuthModal && (
          <AuthModal onClose={() => setShowAuthModal(false)} />
        )}
      </div>
    );
  }

  const listingTypes = [
    { value: 'sublet', label: 'Sublet (Temporary rental of your apartment)' },
    { value: 'roommate', label: 'Roommate Wanted (Share your apartment)' },
    { value: 'lease_transfer', label: 'Lease Transfer (Transfer your lease to someone new)' }
  ];

  const amenitiesList = [
    'Air Conditioning', 'Dishwasher', 'In-unit Laundry', 'Gym', 'Rooftop',
    'Doorman', 'Elevator', 'Balcony', 'Hardwood Floors', 'High Ceilings',
    'Walk-in Closet', 'Storage', 'Parking', 'Bike Storage', 'Package Room'
  ];

  const boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleAmenityToggle = (amenity) => {
    setFormData(prev => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter(a => a !== amenity)
        : [...prev.amenities, amenity]
    }));
  };

  const handleImageUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploadingImages(true);
    
    try {
      const uploadedImageUrls = [];
      const imageFiles = [];
      
      for (const file of files) {
        // Create preview URL
        const previewUrl = URL.createObjectURL(file);
        
        // Prepare file data for upload
        const formData = new FormData();
        formData.append('image', file);
        formData.append('listing_id', 'temp_' + Date.now());
        
        // For now, create preview and store file info
        // Real upload will happen on form submission
        uploadedImageUrls.push(previewUrl);
        imageFiles.push(file);
      }
      
      setImagePreview(prev => [...prev, ...uploadedImageUrls]);
      setFormData(prev => ({ 
        ...prev, 
        uploaded_image_files: [...prev.uploaded_image_files, ...imageFiles]
      }));
      
    } catch (error) {
      console.error('Error uploading images:', error);
      alert('Failed to upload images. Please try again.');
    } finally {
      setUploadingImages(false);
    }
  };

  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 3));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // First, upload images if any
      let uploadedImageUrls = [];
      
      if (formData.uploaded_image_files.length > 0) {
        setUploadingImages(true);
        
        for (const file of formData.uploaded_image_files) {
          const imageFormData = new FormData();
          imageFormData.append('image', file);
          imageFormData.append('user_id', user?.id || 'anonymous');
          
          try {
            const imageResponse = await axios.post(`${API}/upload/image`, imageFormData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
            
            if (imageResponse.data.success) {
              uploadedImageUrls.push(imageResponse.data.image_url);
            }
          } catch (imageError) {
            console.error('Image upload failed:', imageError);
          }
        }
        setUploadingImages(false);
      }

      // Submit the listing with uploaded image URLs
      const response = await axios.post(`${API}/tenant/list-apartment`, {
        ...formData,
        images: uploadedImageUrls,
        uploaded_image_files: undefined, // Remove file objects from submission
        user_id: user?.id || 'anonymous',
        user_email: user?.email || formData.contact_email,
        submitted_at: new Date().toISOString()
      });

      if (response.data.success) {
        setSubmitted(true);
      } else {
        alert('Failed to submit listing. Please try again.');
      }
    } catch (error) {
      console.error('Submission error:', error);
      alert('Failed to submit listing. Please check your information and try again.');
    } finally {
      setSubmitting(false);
      setUploadingImages(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Your Apartment Listing Has Been Submitted!
            </h2>
            <p className="text-gray-600 mb-6">
              Thank you for submitting your apartment listing. Our team will review your submission and contact you within 24 hours.
            </p>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-orange-800 mb-2">What's Next?</h3>
              <ul className="text-sm text-orange-700 space-y-1">
                <li>• We'll verify your listing details</li>
                <li>• Your listing will go live within 24-48 hours</li>
                <li>• You'll receive inquiries at {formData.contact_email}</li>
                <li>• We'll help you find the perfect tenant or roommate</li>
              </ul>
            </div>
            <button
              onClick={() => window.location.href = '/'}
              className="bg-orange-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors"
            >
              Return to Homepage
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              🏠 List Your Apartment
            </h1>
            <p className="text-xl text-gray-600 mb-2">
              Sublet, find roommates, or transfer your lease - all with zero fees!
            </p>
            <p className="text-gray-500">
              Whether you're traveling, need a roommate, or moving out early, we'll help you find the perfect solution.
            </p>
          </div>

          {/* Progress Indicator */}
          <div className="flex items-center justify-center mb-8">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  currentStep >= step 
                    ? 'bg-orange-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {step}
                </div>
                {step < 3 && (
                  <div className={`h-1 w-16 mx-2 ${
                    currentStep > step ? 'bg-orange-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>

          {/* Form */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <form onSubmit={handleSubmit}>
              {/* Step 1: Basic Information */}
              {currentStep === 1 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Basic Information</h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Listing Type *
                      </label>
                      <select
                        name="listing_type"
                        value={formData.listing_type}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        required
                      >
                        {listingTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Rent Price (per month) *
                      </label>
                      <div className="relative">
                        <span className="absolute left-3 top-2 text-gray-500">$</span>
                        <input
                          type="number"
                          name="rent_price"
                          value={formData.rent_price}
                          onChange={handleInputChange}
                          className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                          placeholder="2500"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Listing Title *
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="e.g., Beautiful 1BR Sublet in SoHo Available June-August"
                      required
                    />
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description *
                    </label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows="4"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="Describe your apartment, why you're renting it out, and what makes it special..."
                      required
                    />
                  </div>

                  <div className="grid md:grid-cols-3 gap-6 mt-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Bedrooms *
                      </label>
                      <select
                        name="bedrooms"
                        value={formData.bedrooms}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        required
                      >
                        <option value="">Select</option>
                        <option value="0">Studio</option>
                        <option value="1">1 Bedroom</option>
                        <option value="2">2 Bedrooms</option>
                        <option value="3">3 Bedrooms</option>
                        <option value="4+">4+ Bedrooms</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Bathrooms *
                      </label>
                      <select
                        name="bathrooms"
                        value={formData.bathrooms}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        required
                      >
                        <option value="">Select</option>
                        <option value="1">1 Bathroom</option>
                        <option value="1.5">1.5 Bathrooms</option>
                        <option value="2">2 Bathrooms</option>
                        <option value="2.5">2.5 Bathrooms</option>
                        <option value="3+">3+ Bathrooms</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Square Feet
                      </label>
                      <input
                        type="number"
                        name="sqft"
                        value={formData.sqft}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        placeholder="800"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Location & Dates */}
              {currentStep === 2 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Location & Availability</h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Street Address *
                      </label>
                      <input
                        type="text"
                        name="address"
                        value={formData.address}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        placeholder="123 Main Street, Apt 4B"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Neighborhood *
                      </label>
                      <input
                        type="text"
                        name="neighborhood"
                        value={formData.neighborhood}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        placeholder="SoHo, Upper East Side, Williamsburg"
                        required
                      />
                    </div>
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Borough *
                    </label>
                    <select
                      name="borough"
                      value={formData.borough}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      required
                    >
                      {boroughs.map(borough => (
                        <option key={borough} value={borough}>
                          {borough}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6 mt-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Available Date *
                      </label>
                      <input
                        type="date"
                        name="available_date"
                        value={formData.available_date}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        {formData.listing_type === 'lease_transfer' ? 'Lease End Date' : 'End Date (if temporary)'}
                      </label>
                      <input
                        type="date"
                        name="lease_end_date"
                        value={formData.lease_end_date}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Amenities */}
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-4">
                      Amenities (select all that apply)
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {amenitiesList.map(amenity => (
                        <label key={amenity} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.amenities.includes(amenity)}
                            onChange={() => handleAmenityToggle(amenity)}
                            className="mr-2 h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                          />
                          <span className="text-sm text-gray-700">{amenity}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Additional Options */}
                  <div className="mt-6 grid md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          name="utilities_included"
                          checked={formData.utilities_included}
                          onChange={handleInputChange}
                          className="mr-2 h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                        />
                        <span className="text-sm text-gray-700">Utilities included in rent</span>
                      </label>
                      
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          name="furnished"
                          checked={formData.furnished}
                          onChange={handleInputChange}
                          className="mr-2 h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                        />
                        <span className="text-sm text-gray-700">Furnished</span>
                      </label>
                    </div>
                    
                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          name="pets_allowed"
                          checked={formData.pets_allowed}
                          onChange={handleInputChange}
                          className="mr-2 h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                        />
                        <span className="text-sm text-gray-700">Pets allowed</span>
                      </label>
                      
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          name="short_term_ok"
                          checked={formData.short_term_ok}
                          onChange={handleInputChange}
                          className="mr-2 h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                        />
                        <span className="text-sm text-gray-700">Short-term rentals OK</span>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Contact & Images */}
              {currentStep === 3 && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Contact Information & Photos</h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Your Name *
                      </label>
                      <input
                        type="text"
                        name="contact_name"
                        value={formData.contact_name}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        placeholder="John Smith"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        name="contact_email"
                        value={formData.contact_email}
                        onChange={handleInputChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        placeholder="john@example.com"
                        required
                      />
                    </div>
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      name="contact_phone"
                      value={formData.contact_phone}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="+1 (555) 123-4567"
                      required
                    />
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Security Deposit Required
                    </label>
                    <input
                      type="text"
                      name="deposit_required"
                      value={formData.deposit_required}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="e.g., First month's rent, $500, None"
                    />
                  </div>

                  {/* Photo Upload */}
                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Apartment Photos *
                    </label>
                    <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg">
                      <div className="space-y-1 text-center">
                        <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        <div className="flex text-sm text-gray-600">
                          <label htmlFor="images" className={`relative cursor-pointer bg-white rounded-md font-medium text-orange-600 hover:text-orange-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-orange-500 ${uploadingImages ? 'pointer-events-none opacity-50' : ''}`}>
                            <span>{uploadingImages ? 'Uploading...' : 'Upload photos'}</span>
                            <input
                              id="images"
                              name="images"
                              type="file"
                              className="sr-only"
                              multiple
                              accept="image/*"
                              onChange={handleImageUpload}
                              disabled={uploadingImages}
                            />
                          </label>
                          <p className="pl-1">or drag and drop</p>
                        </div>
                        <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB each</p>
                        <p className="text-xs text-orange-600 font-medium">Photos help your listing get 5x more responses!</p>
                      </div>
                    </div>
                    {imagePreview.length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm text-gray-600 mb-2">{imagePreview.length} photo(s) selected</p>
                        <div className="grid grid-cols-3 gap-4">
                          {imagePreview.map((url, index) => (
                            <div key={index} className="relative">
                              <img
                                src={url}
                                alt={`Preview ${index + 1}`}
                                className="h-24 w-full object-cover rounded-lg"
                              />
                              <button
                                type="button"
                                onClick={() => {
                                  const newPreviews = imagePreview.filter((_, i) => i !== index);
                                  const newFiles = formData.uploaded_image_files.filter((_, i) => i !== index);
                                  setImagePreview(newPreviews);
                                  setFormData(prev => ({ ...prev, uploaded_image_files: newFiles }));
                                }}
                                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mt-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Additional Notes
                    </label>
                    <textarea
                      name="additional_notes"
                      value={formData.additional_notes}
                      onChange={handleInputChange}
                      rows="3"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                      placeholder="Any additional information potential tenants should know..."
                    />
                  </div>
                </div>
              )}

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-8">
                <button
                  type="button"
                  onClick={prevStep}
                  disabled={currentStep === 1}
                  className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                    currentStep === 1
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-gray-600 text-white hover:bg-gray-700'
                  }`}
                >
                  Previous
                </button>

                {currentStep < 3 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    className="px-6 py-2 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 transition-colors"
                  >
                    Next Step
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-8 py-2 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 transition-colors disabled:bg-gray-400"
                  >
                    {submitting ? 'Submitting...' : 'Submit Listing'}
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TenantListingPage;