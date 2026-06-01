import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

const customStyle = {
  ...oneDark,
  'pre[class*="language-"]': {
    ...oneDark['pre[class*="language-"]'],
    background: 'rgba(0, 0, 0, 0.3)',
    borderRadius: '0.5rem',
    padding: '1rem',
    margin: '1rem 0',
  },
  'code[class*="language-"]': {
    ...oneDark['code[class*="language-"]'],
    background: 'transparent',
  },
}

export default function MarkdownRenderer({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="text-2xl font-heading font-bold text-neon-cyan mb-4 mt-6 first:mt-0">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-heading font-semibold text-neon-cyan mb-3 mt-5">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-heading font-medium text-neon-cyan mb-2 mt-4">
            {children}
          </h3>
        ),
        p: ({ children }) => (
          <p className="text-gray-300 mb-3 leading-relaxed">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc list-inside mb-3 space-y-1 text-gray-300">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-300">
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li className="text-gray-300">{children}</li>
        ),
        code: ({ inline, className, children }) => {
          if (inline) {
            return (
              <code className="bg-bg-primary px-1.5 py-0.5 rounded text-neon-cyan font-mono text-sm">
                {children}
              </code>
            )
          }
          return (
            <SyntaxHighlighter
              style={customStyle}
              language={className?.replace('language-', '') || 'text'}
              PreTag="div"
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          )
        },
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-neon-cyan pl-4 my-3 italic text-gray-400">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-4">
            <table className="min-w-full border border-white/10 rounded-lg overflow-hidden">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-white/5">{children}</thead>
        ),
        th: ({ children }) => (
          <th className="px-4 py-2 text-left text-neon-cyan font-heading text-sm border-b border-white/10">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-4 py-2 text-gray-300 text-sm border-b border-white/10">
            {children}
          </td>
        ),
        a: ({ href, children }) => (
          <a 
            href={href} 
            className="text-neon-cyan hover:underline"
            target="_blank" 
            rel="noopener noreferrer"
          >
            {children}
          </a>
        ),
        hr: () => <hr className="border-white/10 my-4" />,
        strong: ({ children }) => (
          <strong className="text-white font-semibold">{children}</strong>
        ),
        em: ({ children }) => (
          <em className="text-gray-400">{children}</em>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}