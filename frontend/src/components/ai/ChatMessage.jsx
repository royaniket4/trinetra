import { motion } from 'framer-motion'
import { User, Bot } from 'lucide-react'
import StreamingMessage from './StreamingMessage'

const messageVariants = {
  hidden: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0 },
}

export default function ChatMessage({ message, index, isStreaming }) {
  const { role, content, timestamp } = message

  const formattedTime = timestamp 
    ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : null

  if (role === 'user') {
    return (
      <motion.div
        variants={messageVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: index * 0.05 }}
        className="flex gap-3 justify-end"
      >
        <div className="max-w-[85%] rounded-xl p-4 bg-electric-blue/20 text-white border border-electric-blue/20">
          <div className="text-sm whitespace-pre-wrap leading-relaxed">{content}</div>
        </div>
        <div className="w-10 h-10 rounded-full bg-electric-blue/20 flex items-center justify-center flex-shrink-0">
          <User className="w-5 h-5 text-electric-blue" />
        </div>
      </motion.div>
    )
  }

  return (
    <StreamingMessage 
      content={content} 
      isStreaming={isStreaming && index === 0}
    />
  )
}