'use client';

import { motion } from 'framer-motion';
import { FiUserCheck, FiMessageCircle } from 'react-icons/fi';
import Link from 'next/link';

const fade = {
  hidden: { opacity: 0, y: 8 },
  show: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.05 * i, type: 'spring', stiffness: 120, damping: 16 },
  }),
};

export default function HomePage() {
  return (
    <main className="min-h-[calc(100svh-64px)] bg-gradient-to-br from-indigo-50 via-white to-pink-50">
      <div className="relative mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="mb-6 flex flex-col gap-3 md:flex-row md:items-start md:justify-between"
          variants={fade}
          initial="hidden"
          animate="show"
        >
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Personality Test</h1>
            <p className="mt-1 text-sm text-gray-600">Choose your analysis method</p>
          </div>
        </motion.div>

        {/* Card layout */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Self/Guided Analysis Card */}
          <motion.div
            variants={fade}
            custom={1}
            initial="hidden"
            animate="show"
            className="flex flex-col items-center justify-center p-6 bg-white rounded-lg shadow-lg cursor-pointer hover:shadow-xl"
          >
            <FiUserCheck className="text-4xl text-indigo-600" />
            <h3 className="mt-4 text-lg font-semibold">Self/Guided Analysis</h3>
            <p className="text-center mt-2 text-sm text-gray-500">
              Analyze your personality based on guided questions.
            </p>
            <Link href="/self-analysis"className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-full">Start Guided Analysis</Link>
          </motion.div>

          {/* Chat/Free Analysis Card */}
          <motion.div
            variants={fade}
            custom={2}
            initial="hidden"
            animate="show"
            className="flex flex-col items-center justify-center p-6 bg-white rounded-lg shadow-lg cursor-pointer hover:shadow-xl"
          >
            <FiMessageCircle className="text-4xl text-indigo-600" />
            <h3 className="mt-4 text-lg font-semibold">Chat/Free Analysis</h3>
            <p className="text-center mt-2 text-sm text-gray-500">
              Talk to our agent to get self-analyzed.
            </p>
            <Link href="/free-analysis" className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-full">Start Chat Analysis</Link>
          </motion.div>
        </div>
      </div>
    </main>
  );
}
