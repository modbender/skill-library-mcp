import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { LoadingBar } from '@/components/ui/loading-bar'

export default function PaperLoading() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      <Sidebar />
      <div className="sticky top-16 z-40">
        <LoadingBar />
      </div>
      <main className="md:ml-64">
        <div className="max-w-5xl mx-auto px-4 py-6 animate-fade-in">
          <div className="skeleton h-4 w-1/3 mb-4" />
          <div className="flex gap-6">
            <div className="flex-1 space-y-4">
              <div className="skeleton h-56 w-full" />
              <div className="skeleton h-6 w-2/3" />
              <div className="skeleton h-4 w-full" />
              <div className="skeleton h-4 w-5/6" />
              <div className="skeleton h-4 w-4/6" />
              <div className="skeleton h-48 w-full" />
            </div>
            <aside className="hidden lg:block w-80 space-y-4">
              <div className="skeleton h-40 w-full" />
              <div className="skeleton h-52 w-full" />
              <div className="skeleton h-32 w-full" />
            </aside>
          </div>
        </div>
      </main>
    </div>
  )
}
