import React from 'react'

/**
 * Help page - support and documentation
 *
 * FAQs and getting started guides
 *
 * @returns {React.ReactElement} Help page component
 *
 * @example
 * ```tsx
 * <HelpPage />
 * ```
 */
export function HelpPage(): React.ReactElement {
  const faqs = [
    {
      question: 'How do I connect my social media accounts?',
      answer: 'Go to the Connectors page and click the button for each platform you want to connect.',
    },
    {
      question: 'Can I schedule posts in advance?',
      answer: 'Yes! Use the Publishing page to schedule posts across all your connected platforms.',
    },
    {
      question: 'How does the AI content generator work?',
      answer: 'The AI Generator page lets you describe your content idea, and AI will help create it.',
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Help & Support</h1>

      <div className="max-w-2xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <details key={i} className="bg-slate-900 border border-slate-800 rounded-lg p-4 group">
                <summary className="font-semibold text-white cursor-pointer group-open:text-purple-400 transition-colors">
                  {faq.question}
                </summary>
                <p className="text-slate-400 mt-2">{faq.answer}</p>
              </details>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-2">Need more help?</h2>
          <p className="text-slate-400 mb-4">Contact support at support@thefeed.com</p>
        </div>
      </div>
    </div>
  )
}
