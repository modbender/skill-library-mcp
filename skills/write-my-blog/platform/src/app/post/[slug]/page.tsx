import { getDatabase } from "@/lib/db";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

async function renderMarkdown(md: string): Promise<string> {
    let html = md
        .replace(/^### (.+)$/gm, "<h3>$1</h3>")
        .replace(/^## (.+)$/gm, "<h2>$1</h2>")
        .replace(/^# (.+)$/gm, "<h1>$1</h1>")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/`(.+?)`/g, "<code>$1</code>")
        .replace(/^\- (.+)$/gm, "<li>$1</li>")
        .replace(/^\* (.+)$/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
        .replace(/^(?!<[hulo])((?!<).+)$/gm, "<p>$1</p>")
        .replace(/<p><\/p>/g, "");
    return html;
}

export default async function PostPage({ params }: { params: { slug: string } }) {
    const db = await getDatabase();
    const post = await db.getPost(params.slug);
    if (!post || post.status !== "published") notFound();

    // Increment view
    await db.updatePost(post.id, {});

    const html = await renderMarkdown(post.content);

    return (
        <div className="wrap">
            <nav style={{ padding: "1.5rem 0" }}>
                <a href="/" style={{ fontSize: "0.85rem" }}>← Back to blog</a>
            </nav>

            <article>
                <div className="post-meta" style={{ marginBottom: "0.75rem" }}>
                    <span>{post.authorName}</span>
                    {" · "}
                    <span>{new Date(post.createdAt).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</span>
                    {" · "}
                    <span>{post.viewCount + 1} views</span>
                </div>

                <h1 style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>{post.title}</h1>

                {post.tags && post.tags.length > 0 && (
                    <div className="tags" style={{ marginBottom: "2rem" }}>
                        {post.tags.map((tag) => (
                            <span key={tag} className="tag">{tag}</span>
                        ))}
                    </div>
                )}

                <div className="post-body" dangerouslySetInnerHTML={{ __html: html }} />
            </article>

            <footer className="blog-footer">
                Powered by <strong>Write My Blog</strong> — an OpenClaw skill
            </footer>
        </div>
    );
}
