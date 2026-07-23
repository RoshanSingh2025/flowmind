import { Architecture } from "@/components/landing/architecture";
import { Demo } from "@/components/landing/demo";
import { Features } from "@/components/landing/features";
import { Footer } from "@/components/landing/footer";
import { Hero } from "@/components/landing/hero";
import { Navbar } from "@/components/landing/navbar";

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-x-hidden">
      <Navbar />
      <Hero />
      <Features />
      <Architecture />
      <Demo />
      <Footer />
    </main>
  );
}
