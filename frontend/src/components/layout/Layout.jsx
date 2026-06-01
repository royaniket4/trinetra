import { Outlet } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { X, Brain } from 'lucide-react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { useWebSocket } from '../../hooks/useWebSocket'
import TrinetraMind from '../ai/TrinetraMind'
import useStore from '../../store/useStore'

export default function Layout() {
  useWebSocket()
  const { aiPanelOpen, toggleAiPanel } = useStore()
  console.log('Layout render - aiPanelOpen:', aiPanelOpen)

  return (
    <div className="min-h-screen bg-bg-primary grid-bg">
      <Sidebar />
      <TopBar />
      <main className="ml-64 pt-16 min-h-screen relative">
        <div className="p-6">
          <Outlet />
        </div>
      </main>

      <AnimatePresence>
        {aiPanelOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 w-[900px] bg-bg-secondary border-l border-white/10 z-50 shadow-2xl"
          >
            <div className="h-full flex flex-col">
              <div className="flex items-center justify-between p-4 border-b border-white/10 bg-bg-secondary/90">
                <div className="flex items-center gap-2">
                  <span className="text-neon-cyan font-heading text-lg">🧠 TrinetraMind</span>
                  <span className="px-2 py-0.5 text-xs rounded-full bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30">
                    AI Assistant
                  </span>
                </div>
                <button
                  onClick={toggleAiPanel}
                  className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-hidden">
                <TrinetraMind />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {aiPanelOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 z-40"
          onClick={toggleAiPanel}
        />
      )}

      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleAiPanel}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-neon-cyan to-electric-blue flex items-center justify-center shadow-lg shadow-neon-cyan/30 z-30 hover:shadow-neon-cyan/50 transition-shadow"
      >
        <div className="absolute inset-0 rounded-full animate-ping bg-neon-cyan/30 opacity-75" />
        <Brain className="w-6 h-6 text-white relative z-10" />
      </motion.button>
    </div>
  )
}