import Link from "next/link";

export default function NotFound() {
  return (
    <section className="rounded border border-line bg-white p-6">
      <h1 className="text-xl font-semibold">Component not found</h1>
      <p className="mt-2 text-sm text-muted">That CPI item code is not in the current registry.</p>
      <Link className="mt-4 inline-block rounded bg-teal px-3 py-2 text-sm text-white" href="/components">
        Back to components
      </Link>
    </section>
  );
}
