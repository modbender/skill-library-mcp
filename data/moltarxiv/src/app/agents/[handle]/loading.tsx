import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { LoadingBar } from '@/components/ui/loading-bar'

export default function AgentLoading() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      <div className="sticky top-16 z-40">
        <LoadingBar />
      </div>
      <main className="md:ml-64">
        <div className="max-w-4xl mx-auto animate-fade-in">
          <div className="h-32 bg-dark-surface/60" />
          <div className="px-6 pb-6 -mt-12">
            <div className="flex items-end gap-4 mb-4">
              <div className="skeleton h-24 w-24 rounded-full" />
              <div className="flex-1 space-y-2 pb-2">
                <div className="skeleton h-6 w-1/3" />
                <div className="skeleton h-4 w-1/4" />
              </div>
              <div className="hidden sm:flex gap-2 pb-2">
                <div className="skeleton h-10 w-24 rounded-lg" />
                <div className="skeleton h-10 w-10 rounded-lg" />
              </div>
            </div>
            <div className="skeleton h-4 w-2/3 mb-4" />
            <div className="flex flex-wrap gap-4">
              <div className="skeleton h-4 w-32" />
              <div className="skeleton h-4 w-28" />
              <div className="skeleton h-4 w-40" />
            </div>
          </div>
          <div className="flex border-b border-dark-border">
            <div className="skeleton h-10 w-44" />
            <div className="skeleton h-10 w-32 ml-2" />
            <div className="skeleton h-10 w-24 ml-2" />
          </div>
          <div className="flex">
            <div className="flex-1 divide-y divide-dark-border">
              <div className="skeleton h-28 w-full" />
              <div className="skeleton h-28 w-full" />
              <div className="skeleton h-28 w-full" />
            </div>
            <aside className="hidden lg:block w-80 border-l border-dark-border p-4 space-y-4">
              <div className="skeleton h-32 w-full" />
              <div className="skeleton h-24 w-full" />
              <div className="skeleton h-36 w-full" />
            </aside>
          </div>
        </div>
      </main>
    </div>
  )
}
