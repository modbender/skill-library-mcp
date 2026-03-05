import { LoadingBar } from '@/components/ui/loading-bar'

export default function GlobalLoading() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <div className="sticky top-0 z-50">
        <LoadingBar />
      </div>
    </div>
  )
}
