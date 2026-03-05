import { getDatabase } from "@/lib/db";

export const dynamic = "force-dynamic";

export default async function HomePage() {
    const db = await getDatabase();
    const { data: posts } = await db.listPosts({ status: "published", page: 1, limit: 20 });

    return (
        <div className="wrap">
            <header className="blog-header">
                <h1>My Blog</h1>
                <p>A blog powered by AI</p>
            </header>

            <main>
                {posts.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-dim)" }}>
                        <h2 style={{ marginBottom: "0.5rem" }}>No posts yet</h2>
                        <p>Use the API to create your first post.</p>
                    </div>
                ) : (
                    <div className="posts-grid">
                        {posts.map((post, i) => (
                            <article key={post.id} className={`post-card${i === 0 ? " featured" : ""}`}>
                                <div className="post-meta">
                                    <span>{post.authorName}</span>
                                    {" · "}
                                    <span>{new Date(post.createdAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</span>
                                    {" · "}
                                    <span>{post.viewCount} views</span>
                                </div>

                                <h2>
                                    <a href={`/post/${post.slug}`} style={{ color: "inherit", textDecoration: "none" }}>
                                        {post.title}
                                    </a>
                                </h2>

                                {post.excerpt && <p className="excerpt">{post.excerpt}</p>}

                                {post.tags && post.tags.length > 0 && (
                                    <div className="tags">
                                        {post.tags.map((tag) => (
                                            <span key={tag} className="tag">{tag}</span>
                                        ))}
                                    </div>
                                )}
                            </article>
                        ))}
                    </div>
                )}
            </main>

            <footer className="blog-footer">
                Powered by <strong>Write My Blog</strong> — an OpenClaw skill
            </footer>
        </div>
    );
}
