import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { PageWordMark } from './WordMark';

// About Us Page
export const AboutUsPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="mb-8">
            <PageWordMark 
              linkTo="/"
              tagline="ABOUT OUR COMPANY"
              hover={false}
            />
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Our Mission</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            We're transforming apartment hunting in NYC to be transparent, affordable, and stress-free.
          </p>
        </div>

        {/* Content */}
        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Our Story</h2>
            <div className="space-y-4 text-gray-700">
              <p>
                Founded in 2025, NoFeePlaces was born from a simple frustration: why should renters pay 
                thousands in broker fees for something they can do themselves?
              </p>
              <p>
                After experiencing the painful process of paying $4,000+ in broker fees for a Manhattan 
                apartment, our founders decided to create a better way. We built a platform where 
                landlords can list directly, and renters can find amazing apartments without the 
                traditional broker markup.
              </p>
              <p>
                Today, we've helped thousands of New Yorkers save millions in unnecessary fees while 
                finding their perfect home.
              </p>
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
            <div className="text-center">
              <div className="text-5xl mb-4">🏙️</div>
              <h3 className="text-2xl font-bold mb-4">Our Impact</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Money Saved</span>
                  <span className="font-bold">$2M+</span>
                </div>
                <div className="flex justify-between">
                  <span>Apartments Listed</span>
                  <span className="font-bold">400+</span>
                </div>
                <div className="flex justify-between">
                  <span>Happy Renters</span>
                  <span className="font-bold">1,000+</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Values */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Our Values</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-4xl mb-4">💡</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Transparency</h3>
              <p className="text-gray-600">
                Every listing shows real prices, real contact info, and real availability. 
                No hidden fees, no surprises.
              </p>
            </div>
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Trust</h3>
              <p className="text-gray-600">
                We verify our listings and work directly with property owners to ensure 
                authenticity and reliability.
              </p>
            </div>
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Simplicity</h3>
              <p className="text-gray-600">
                Finding an apartment should be easy. We've built tools that make the 
                process straightforward and efficient.
              </p>
            </div>
          </div>
        </div>

        {/* Professional CTA */}
        <div className="text-center bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 rounded-2xl p-8 text-white border border-slate-600 shadow-2xl">
          <h2 className="text-2xl font-bold mb-4">Ready to Save on Your Next Apartment?</h2>
          <p className="mb-6 text-gray-200 font-medium">
            Join thousands of New Yorkers who've found their perfect home without paying broker fees.
          </p>
          <Link
            to="/"
            className="inline-flex items-center bg-white text-slate-800 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl border border-gray-200"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Start Your Search
          </Link>
        </div>
      </div>
    </div>
  );
};

// Why No Fee Page
export const WhyNoFeePage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Why No Fee Apartments?</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Understanding the traditional broker system and how we're changing the game.
          </p>
        </div>

        {/* Traditional vs No Fee Comparison */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
            <div className="text-center mb-6">
              <div className="text-4xl mb-2">😤</div>
              <h3 className="text-xl font-bold text-red-800">Traditional Broker Fees</h3>
            </div>
            <ul className="space-y-3 text-red-700">
              <li className="flex items-center">
                <span className="text-red-500 mr-2">❌</span>
                15% of annual rent (often $3,000-$6,000)
              </li>
              <li className="flex items-center">
                <span className="text-red-500 mr-2">❌</span>
                Due upfront with security deposit
              </li>
              <li className="flex items-center">
                <span className="text-red-500 mr-2">❌</span>
                Limited apartment access
              </li>
              <li className="flex items-center">
                <span className="text-red-500 mr-2">❌</span>
                Pressure to decide quickly
              </li>
              <li className="flex items-center">
                <span className="text-red-500 mr-2">❌</span>
                Broker controls the process
              </li>
            </ul>
          </div>

          <div className="bg-green-50 border-2 border-green-200 rounded-xl p-6">
            <div className="text-center mb-6">
              <div className="text-4xl mb-2">😊</div>
              <h3 className="text-xl font-bold text-green-800">No Fee Apartments</h3>
            </div>
            <ul className="space-y-3 text-green-700">
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                $0 broker fees - ever!
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                More money for your deposit & moving
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                Direct access to landlords
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                Take your time to decide
              </li>
              <li className="flex items-center">
                <span className="text-green-500 mr-2">✅</span>
                You control your search
              </li>
            </ul>
          </div>
        </div>

        {/* Savings Calculator */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">Your Potential Savings</h2>
          <div className="grid sm:grid-cols-3 gap-6 text-center">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-2">$2,500/mo</div>
              <div className="text-sm text-gray-600 mb-2">Studio Rent</div>
              <div className="text-lg font-semibold text-green-600">Save: $3,750</div>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-2">$3,200/mo</div>
              <div className="text-sm text-gray-600 mb-2">1BR Rent</div>
              <div className="text-lg font-semibold text-green-600">Save: $4,800</div>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600 mb-2">$4,500/mo</div>
              <div className="text-sm text-gray-600 mb-2">2BR Rent</div>
              <div className="text-lg font-semibold text-green-600">Save: $6,750</div>
            </div>
          </div>
          <p className="text-center text-gray-600 mt-6 text-sm">
            *Based on 15% broker fee calculation
          </p>
        </div>

        {/* FAQ */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">Common Questions</h2>
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-bold text-gray-900 mb-2">Are no-fee apartments lower quality?</h3>
              <p className="text-gray-700">
                Not at all! Many of our listings are luxury buildings and well-maintained properties. 
                The difference is that landlords pay us directly instead of charging tenants.
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-bold text-gray-900 mb-2">How do you make money?</h3>
              <p className="text-gray-700">
                We charge landlords a small listing fee and take a percentage of successful rentals. 
                This aligns our interests - we only succeed when you find a great apartment.
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-bold text-gray-900 mb-2">Is there a catch?</h3>
              <p className="text-gray-700">
                No catch! You might need to do a bit more of the legwork yourself (scheduling viewings, 
                asking questions), but most renters prefer this level of control anyway.
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-green-500 to-teal-600 rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Ready to Skip the Broker Fees?</h2>
          <p className="mb-6 opacity-90">
            Browse 400+ verified no-fee apartments across all NYC boroughs.
          </p>
          <Link
            to="/"
            className="inline-block bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors mr-4"
          >
            Browse Apartments
          </Link>
          <Link
            to="/contact"
            className="inline-block border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-green-600 transition-colors"
          >
            Contact Us
          </Link>
        </div>
      </div>
    </div>
  );
};

// Contact Us Page
export const ContactUsPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Handle form submission here
    setSubmitted(true);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header with Logo */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <PageWordMark />
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Contact Us</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Have questions? We're here to help! Reach out to us anytime.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Send Us a Message</h2>
            
            {submitted ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">✅</div>
                <h3 className="text-xl font-bold text-green-600 mb-2">Message Sent!</h3>
                <p className="text-gray-600">We'll get back to you within 24 hours.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                  <select
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select a subject</option>
                    <option value="general">General Inquiry</option>
                    <option value="listing">Listing Questions</option>
                    <option value="technical">Technical Support</option>
                    <option value="partnership">Partnership Opportunities</option>
                    <option value="feedback">Feedback</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                  <textarea
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows="5"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  ></textarea>
                </div>
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                >
                  Send Message
                </button>
              </form>
            )}
          </div>

          {/* Contact Information */}
          <div className="space-y-8">
            {/* Quick Contact */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Get in Touch</h2>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">Email</div>
                    <div className="text-blue-600">placesfirm@gmail.com</div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">Phone</div>
                    <div className="text-green-600">+1-646-408-8048</div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">Location</div>
                    <div className="text-purple-600">New York City, NY</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Response Times */}
            <div className="bg-gradient-to-br from-teal-500 to-blue-600 rounded-2xl p-8 text-white">
              <h3 className="text-xl font-bold mb-4">Response Times</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>General Inquiries</span>
                  <span className="font-semibold">24 hours</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Listing Questions</span>
                  <span className="font-semibold">4 hours</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Technical Support</span>
                  <span className="font-semibold">2 hours</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Emergency Issues</span>
                  <span className="font-semibold">1 hour</span>
                </div>
              </div>
            </div>

            {/* Office Hours */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Office Hours</h3>
              <div className="space-y-2 text-gray-700">
                <div className="flex justify-between">
                  <span>Monday - Friday</span>
                  <span>9:00 AM - 7:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>Saturday</span>
                  <span>10:00 AM - 6:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span>Sunday</span>
                  <span>12:00 PM - 5:00 PM</span>
                </div>
              </div>
              <p className="text-sm text-gray-500 mt-4">
                *All times are Eastern Standard Time (EST)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Let's Talk Page
export const LetsTalkPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Page Header with Logo */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <PageWordMark />
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Let's Talk!</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Whether you're a renter, landlord, or partner - we'd love to hear from you.
          </p>
        </div>

        {/* Contact Options */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {/* For Renters */}
          <div className="bg-white rounded-2xl shadow-lg p-8 transform hover:scale-105 transition-transform duration-200">
            <div className="text-center mb-6">
              <div className="text-5xl mb-4">🏠</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">For Renters</h3>
              <p className="text-gray-600">Looking for your next no-fee apartment?</p>
            </div>
            <div className="space-y-4">
              <Link
                to="/"
                className="flex items-center justify-center w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-4 px-6 rounded-xl font-semibold transition-all shadow-lg hover:shadow-xl"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Browse Apartments
              </Link>
              <Link
                to="/contact"
                className="flex items-center justify-center w-full border-2 border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400 py-4 px-6 rounded-xl font-semibold transition-all"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Get Personal Help
              </Link>
            </div>
          </div>

          {/* For Landlords */}
          <div className="bg-white rounded-2xl shadow-lg p-8 transform hover:scale-105 transition-transform duration-200">
            <div className="text-center mb-6">
              <div className="text-5xl mb-4">🏢</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">For Landlords</h3>
              <p className="text-gray-600">Want to list your properties with us?</p>
            </div>
            <div className="space-y-4">
              <Link
                to="/landlord/login"
                className="block w-full bg-green-600 hover:bg-green-700 text-white text-center py-3 px-6 rounded-lg font-semibold transition-colors"
              >
                Landlord Portal
              </Link>
              <a
                href="mailto:placesfirm@gmail.com?subject=Landlord Partnership"
                className="block w-full border-2 border-green-600 text-green-600 hover:bg-green-600 hover:text-white text-center py-3 px-6 rounded-lg font-semibold transition-colors"
              >
                Partnership Inquiry
              </a>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">Quick Actions</h2>
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
            <a
              href="tel:+16464088048"
              className="flex flex-col items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="text-2xl mb-2">📞</div>
              <span className="text-sm font-semibold text-blue-700">Call Us</span>
            </a>
            <a
              href="mailto:placesfirm@gmail.com"
              className="flex flex-col items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <div className="text-2xl mb-2">✉️</div>
              <span className="text-sm font-semibold text-green-700">Email Us</span>
            </a>
            <Link
              to="/contact"
              className="flex flex-col items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <div className="text-2xl mb-2">💬</div>
              <span className="text-sm font-semibold text-purple-700">Contact Form</span>
            </Link>
            <button
              onClick={() => {
                // This could open a feedback modal or redirect to feedback
                alert('Feedback form opening...');
              }}
              className="flex flex-col items-center p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
            >
              <div className="text-2xl mb-2">💡</div>
              <span className="text-sm font-semibold text-orange-700">Feedback</span>
            </button>
          </div>
        </div>

        {/* Contact Information */}
        <div className="text-center bg-gradient-to-r from-gray-800 to-gray-900 rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-bold mb-6">We're Here to Help</h2>
          <div className="grid sm:grid-cols-2 gap-6 max-w-2xl mx-auto">
            <div>
              <div className="font-semibold mb-2">📧 Email</div>
              <div className="text-blue-300">placesfirm@gmail.com</div>
            </div>
            <div>
              <div className="font-semibold mb-2">📱 Phone</div>
              <div className="text-blue-300">+1-646-408-8048</div>
            </div>
          </div>
          <p className="mt-6 text-gray-300 text-sm">
            Available Monday-Sunday, 9 AM - 9 PM EST
          </p>
        </div>
      </div>
    </div>
  );
};