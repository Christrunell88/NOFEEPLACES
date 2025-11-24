import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { FAQSchema } from './AdvancedSchema';

// Rent Affordability Calculator
export const RentCalculator = () => {
  const [income, setIncome] = useState('');
  const [result, setResult] = useState(null);

  const calculateAffordableRent = () => {
    const annualIncome = parseFloat(income);
    if (!annualIncome || annualIncome <= 0) return;

    // 30% rule: rent should be 30% of gross income
    const monthlyIncome = annualIncome / 12;
    const maxRent = monthlyIncome * 0.30;
    const comfortable = monthlyIncome * 0.25;
    const stretching = monthlyIncome * 0.35;

    setResult({
      maxRent: Math.round(maxRent),
      comfortable: Math.round(comfortable),
      stretching: Math.round(stretching),
      monthlyIncome: Math.round(monthlyIncome)
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <Helmet>
        <title>NYC Rent Affordability Calculator | NoFeePlaces</title>
        <meta name="description" content="Calculate how much rent you can afford in NYC based on your income. Free tool with personalized recommendations." />
      </Helmet>

      <h2 className="text-3xl font-bold mb-4 text-gray-900">Rent Affordability Calculator</h2>
      <p className="text-gray-600 mb-6">Find out how much you can afford to spend on rent in NYC</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Annual Gross Income
          </label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-gray-500">$</span>
            <input
              type="number"
              value={income}
              onChange={(e) => setIncome(e.target.value)}
              placeholder="75000"
              className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <button
          onClick={calculateAffordableRent}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Calculate Affordable Rent
        </button>

        {result && (
          <div className="mt-6 space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">✅ Comfortable Budget</h3>
              <p className="text-3xl font-bold text-blue-600">${result.comfortable.toLocaleString()}/mo</p>
              <p className="text-sm text-gray-600 mt-1">25% of your income - Most financial advisors recommend this</p>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-900 mb-2">📊 Maximum Budget (30% Rule)</h3>
              <p className="text-3xl font-bold text-green-600">${result.maxRent.toLocaleString()}/mo</p>
              <p className="text-sm text-gray-600 mt-1">30% of your income - Industry standard maximum</p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-900 mb-2">⚠️ Stretching Budget</h3>
              <p className="text-3xl font-bold text-yellow-600">${result.stretching.toLocaleString()}/mo</p>
              <p className="text-sm text-gray-600 mt-1">35% of your income - Only if necessary</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 mt-4">
              <h4 className="font-semibold mb-2">💡 Tips for NYC Renters:</h4>
              <ul className="text-sm text-gray-700 space-y-2">
                <li>• Most landlords require income to be 40x monthly rent</li>
                <li>• With ${income.toLocaleString()}/year, you qualify for apartments up to ${Math.round((parseFloat(income) / 12) / 40).toLocaleString()}/month by landlord standards</li>
                <li>• No-fee apartments save you 12-15% of annual rent (${Math.round(result.maxRent * 1.5).toLocaleString()} savings!)</li>
                <li>• Consider roommates to access better neighborhoods</li>
              </ul>
            </div>

            <button
              onClick={() => window.location.href = `/search?max_price=${result.maxRent}`}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all"
            >
              Find Apartments in Your Budget
            </button>
          </div>
        )}
      </div>

      <div className="mt-8 text-sm text-gray-500 border-t pt-4">
        <p><strong>How it works:</strong> The 30% rule suggests spending no more than 30% of your gross income on rent. This calculator shows you a comfortable range (25%), the standard maximum (30%), and a stretching budget (35%).</p>
      </div>
    </div>
  );
};

// Broker Fee Savings Calculator
export const SavingsCalculator = () => {
  const [rent, setRent] = useState('');
  const [result, setResult] = useState(null);

  const calculateSavings = () => {
    const monthlyRent = parseFloat(rent);
    if (!monthlyRent || monthlyRent <= 0) return;

    const brokerFee = monthlyRent * 1.5; // 15% or 1.5 months typical
    const annualRent = monthlyRent * 12;
    const fiveYearSavings = brokerFee;
    const tenYearSavings = brokerFee * 2; // Moving every 5 years

    setResult({
      brokerFee: Math.round(brokerFee),
      annualRent: Math.round(annualRent),
      fiveYearSavings: Math.round(fiveYearSavings),
      tenYearSavings: Math.round(tenYearSavings),
      monthlyRent
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <Helmet>
        <title>Broker Fee Savings Calculator | NoFeePlaces</title>
        <meta name="description" content="Calculate how much you save by choosing no-fee apartments in NYC. Avoid broker fees up to 15% of annual rent." />
      </Helmet>

      <h2 className="text-3xl font-bold mb-4 text-gray-900">💰 Broker Fee Savings Calculator</h2>
      <p className="text-gray-600 mb-6">See how much you save by finding no-fee apartments</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Monthly Rent
          </label>
          <div className="relative">
            <span className="absolute left-3 top-3 text-gray-500">$</span>
            <input
              type="number"
              value={rent}
              onChange={(e) => setRent(e.target.value)}
              placeholder="3000"
              className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        <button
          onClick={calculateSavings}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
        >
          Calculate Your Savings
        </button>

        {result && (
          <div className="mt-6 space-y-4">
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg p-6 text-center">
              <p className="text-sm font-medium mb-2">YOU SAVE</p>
              <p className="text-5xl font-bold mb-2">${result.brokerFee.toLocaleString()}</p>
              <p className="text-sm opacity-90">By choosing a no-fee apartment</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 mb-1">Traditional Broker Fee</p>
                <p className="text-2xl font-bold text-gray-900">${result.brokerFee.toLocaleString()}</p>
                <p className="text-xs text-gray-500 mt-1">15% of annual rent</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600 mb-1">No-Fee Apartment</p>
                <p className="text-2xl font-bold text-green-600">$0</p>
                <p className="text-xs text-gray-500 mt-1">Zero broker fees</p>
              </div>
            </div>

            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-3">What you could do with ${result.brokerFee.toLocaleString()}:</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>✅ Furnish your entire apartment</li>
                <li>✅ Pay first month's rent + security deposit</li>
                <li>✅ Build your emergency fund</li>
                <li>✅ Take a vacation</li>
                <li>✅ Invest in your future</li>
              </ul>
            </div>

            <div className="bg-purple-50 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-2">📊 Long-term Savings:</h4>
              <p className="text-sm text-gray-700">
                If you move every 5 years: <strong className="text-purple-600">${result.tenYearSavings.toLocaleString()}</strong> saved over 10 years by choosing no-fee apartments!
              </p>
            </div>

            <button
              onClick={() => window.location.href = `/search?max_price=${result.monthlyRent}`}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all"
            >
              Find No-Fee Apartments at ${result.monthlyRent.toLocaleString()}/mo
            </button>
          </div>
        )}
      </div>

      <div className="mt-8 text-sm text-gray-500 border-t pt-4">
        <p><strong>NYC Broker Fee Facts:</strong> Traditional broker fees range from 12-15% of annual rent, typically 1-1.5 months' rent. By finding no-fee apartments, you save this entire amount.</p>
      </div>
    </div>
  );
};

// FAQ Page Component with Schema
export const FAQPage = () => {
  const faqs = [
    {
      question: "What are no-fee apartments?",
      answer: "No-fee apartments are rental units where the landlord or management company does not charge a broker's fee. This means you save 12-15% of your annual rent (typically 1-1.5 months' rent) that would normally go to a broker. These apartments are directly listed by landlords or management companies."
    },
    {
      question: "How much can I save with no-fee apartments?",
      answer: "On a $3,000/month apartment, you save approximately $4,500 in broker fees. That's money you can use for furniture, moving expenses, security deposit, or savings. Over 10 years of renting in NYC, choosing no-fee apartments every time you move could save you $10,000 or more."
    },
    {
      question: "Are no-fee apartments lower quality?",
      answer: "Absolutely not! No-fee apartments are often managed by professional property management companies or landlords who prefer to handle rentals themselves. Many luxury buildings and newly renovated apartments are available as no-fee. The quality depends on the property itself, not whether there's a broker fee."
    },
    {
      question: "What's the catch with no-fee apartments?",
      answer: "There's no catch! No-fee apartments exist because landlords choose to pay for their own marketing and management instead of requiring tenants to pay broker fees. Some buildings have in-house leasing teams, while others work directly with tenants. The apartments are just as legitimate as any other rental."
    },
    {
      question: "How do I know if a listing is truly no-fee?",
      answer: "All apartments on NoFeePlaces.com are verified as no-fee. We only list apartments where the landlord or management company has confirmed no broker fees will be charged to the tenant. Always confirm 'no-fee' status before viewing any apartment, and get it in writing."
    },
    {
      question: "Can I negotiate rent on no-fee apartments?",
      answer: "Yes! Just like any rental, you can negotiate rent on no-fee apartments. Since there's no broker fee, landlords may have more flexibility. The best times to negotiate are during slower rental seasons (November-February) or if you're willing to sign a longer lease."
    },
    {
      question: "What documents do I need to rent a no-fee apartment?",
      answer: "You'll typically need: proof of income (pay stubs, tax returns), photo ID, rental history/references, credit report, and bank statements. Most landlords require your income to be 40x the monthly rent. Some may require a guarantor if you don't meet income requirements."
    },
    {
      question: "How competitive are no-fee apartments?",
      answer: "No-fee apartments can be competitive, especially in desirable neighborhoods, but so are all NYC apartments. The key is to be prepared with your documents, respond quickly to listings, and be ready to submit an application when you find the right place."
    }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <Helmet>
        <title>Frequently Asked Questions | No-Fee Apartments NYC</title>
        <meta name="description" content="Get answers to common questions about no-fee apartments in NYC. Learn how to save thousands on broker fees and find your perfect apartment." />
      </Helmet>

      <FAQSchema faqs={faqs} />

      <h1 className="text-4xl font-bold mb-4 text-gray-900">Frequently Asked Questions</h1>
      <p className="text-xl text-gray-600 mb-12">Everything you need to know about no-fee apartments in NYC</p>

      <div className="space-y-6">
        {faqs.map((faq, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">{faq.question}</h2>
            <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
          </div>
        ))}
      </div>

      <div className="mt-12 bg-blue-50 rounded-lg p-8 text-center">
        <h3 className="text-2xl font-bold mb-4">Still have questions?</h3>
        <p className="text-gray-700 mb-6">Browse our verified no-fee apartments or contact us for help</p>
        <button
          onClick={() => window.location.href = '/apartments'}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Browse No-Fee Apartments
        </button>
      </div>
    </div>
  );
};

export default { RentCalculator, SavingsCalculator, FAQPage };
